"""Meaningful calculation and HTTP checks for the local project."""
from contextlib import redirect_stdout
from io import StringIO
import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

import data_sharing_game as game
import server


class AnalysisTests(unittest.TestCase):
    def test_three_scenarios_have_expected_equilibria_and_dominance(self):
        expectations = [
            ([('Don\'t Share', 'Don\'t Share')], "Don't Share", 10),
            ([("Share", "Share")], "Share", 16),
            ([("Share", "Share"), ("Don't Share", "Don't Share")], None, 10),
        ]
        for scenario, (pairs, dominant, highest) in zip(server.SCENARIOS, expectations):
            with self.subTest(scenario=scenario["id"]):
                result = server.analyze_scenario(scenario)
                actual = [(o["aStrategy"], o["bStrategy"]) for o in result["outcomes"] if o["isNash"]]
                self.assertEqual(actual, pairs)
                self.assertEqual(result["dominant"], {"A": dominant, "B": dominant})
                self.assertEqual(result["highestTotal"], highest)

    def test_unilateral_changes_and_social_optima_for_all_twelve_outcomes(self):
        for scenario in server.SCENARIOS:
            matrix = scenario["matrix"]
            for outcome in server.analyze_scenario(scenario)["outcomes"]:
                with self.subTest(scenario=scenario["id"], outcome=outcome["id"]):
                    a, b = outcome["aStrategy"], outcome["bStrategy"]
                    self.assertEqual((outcome["a"], outcome["b"]), matrix[a, b])
                    self.assertEqual(outcome["switchA"]["score"], matrix[outcome["switchA"]["strategy"], b][0])
                    self.assertEqual(outcome["switchB"]["score"], matrix[a, outcome["switchB"]["strategy"]][1])
                    self.assertEqual(outcome["switchA"]["gain"], outcome["switchA"]["score"] - outcome["a"])
                    self.assertEqual(outcome["switchB"]["gain"], outcome["switchB"]["score"] - outcome["b"])
                    self.assertEqual(outcome["isNash"], outcome["switchA"]["gain"] <= 0 and outcome["switchB"]["gain"] <= 0)
                    self.assertEqual(outcome["isSocialBest"], outcome["total"] == max(sum(scores) for scores in matrix.values()))

    def test_incentive_is_added_only_to_the_sharing_player(self):
        expected = {(s, t): (a + (3 if s == "Share" else 0), b + (3 if t == "Share" else 0))
                    for (s, t), (a, b) in game.PAYOFFS.items()}
        self.assertEqual(server.SCENARIOS[1]["matrix"], expected)

    def test_scenario_analysis_never_changes_baseline(self):
        original = dict(game.PAYOFFS)
        server.api_payload()
        self.assertEqual(game.PAYOFFS, original)
        self.assertEqual(game.find_nash_equilibria(), [("Don't Share", "Don't Share", (3, 3))])
        output = StringIO()
        with redirect_stdout(output):
            game.run_analysis()
        self.assertIn("(Don't Share, Don't Share) -> payoffs (3, 3)", output.getvalue())

    def test_general_analysis_handles_ties_and_absent_pure_equilibrium(self):
        s, n = game.STRATEGIES
        tied = {(a, b): (2, 2) for a in game.STRATEGIES for b in game.STRATEGIES}
        self.assertEqual(len(game.find_nash_equilibria(tied)), 4)
        self.assertIsNone(game.has_dominant_strategy("A", tied))
        self.assertEqual(len(game.find_socially_best_outcome(tied)), 4)
        matching_pennies = {(s,s):(1,-1), (s,n):(-1,1), (n,s):(-1,1), (n,n):(1,-1)}
        self.assertEqual(game.find_nash_equilibria(matching_pennies), [])


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()

    def test_website_and_analysis_are_served_together(self):
        with urlopen(self.base + "/") as response:
            self.assertIn(b"Shared Interest", response.read())
            self.assertEqual(response.status, 200)
        with urlopen(self.base + "/api/scenarios") as response:
            payload = json.load(response)
        self.assertEqual(payload["source"], "Python")
        self.assertEqual(len(payload["scenarios"]), 3)
        self.assertEqual(payload["scenarios"][2]["equilibria"], ["outcome-0", "outcome-3"])
        for path in ("/static/app.js", "/static/styles.css", "/static/favicon.svg"):
            with self.subTest(path=path), urlopen(self.base + path) as response:
                self.assertEqual(response.status, 200)
                self.assertGreater(len(response.read()), 0)

    def test_server_does_not_expose_source_files(self):
        for path in ("/server.py", "/../README.md", "/static/../server.py"):
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                urlopen(self.base + path)
            self.assertEqual(error.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
