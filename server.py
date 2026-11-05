"""Local website and Python analysis API. Run: python3 server.py"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit

from data_sharing_game import (
    PAYOFFS, STRATEGIES, best_responses_a, best_responses_b,
    find_nash_equilibria, find_socially_best_outcome, has_dominant_strategy,
)

ROOT = Path(__file__).resolve().parent
SHARE, PRIVATE = STRATEGIES

SCENARIOS = (
    {
        "id": "competitive", "number": "01", "name": "Competitive environment",
        "shortName": "Competition", "tagline": "Individual gain comes first.",
        "headline": "A better outcome. A reason not to choose it.",
        "description": "Sharing benefits both organizations. But each can earn more by keeping its own data private, whatever the other chooses.",
        "change": "Original model · no added incentive",
        "assumption": "Receiving a competitor’s data while withholding your own gives the highest individual score: 7.",
        "caption": "Both organizations prefer withholding data regardless of the other’s choice. Mutual non-sharing is the equilibrium, although mutual sharing gives both a higher score.",
        "takeaway": "What is best for each organization individually can leave both worse off together.",
        "matrix": dict(PAYOFFS),
    },
    {
        "id": "incentive", "number": "02", "name": "Sharing incentive",
        "shortName": "Incentives", "tagline": "Change the reward. Change the choice.",
        "headline": "Make sharing the individually better choice.",
        "description": "Add a participation benefit of 3 points whenever an organization shares. The bonus applies even if its competitor does not share.",
        "change": "+3 points to an organization whenever it shares",
        "assumption": "A guaranteed sharing benefit is added to the original scores. Its external funding or resource cost is outside this model.",
        "caption": "An organization receives 3 extra points whenever it shares. Sharing becomes the dominant strategy for both, making mutual sharing the equilibrium.",
        "takeaway": "When the payoff structure rewards cooperation, individual incentives and collective benefit can align.",
        "matrix": {
            (a, b): (pa + (3 if a == SHARE else 0), pb + (3 if b == SHARE else 0))
            for (a, b), (pa, pb) in PAYOFFS.items()
        },
    },
    {
        "id": "conditional", "number": "03", "name": "Trust-dependent cooperation",
        "shortName": "Expectations", "tagline": "Your best choice depends on theirs.",
        "headline": "Two stable outcomes. Expectations matter.",
        "description": "Reduce the one-sided advantage of withholding data from 7 to 4. Sharing is now best when the other shares; withholding is best when the other withholds.",
        "change": "One-sided withholding payoff: 7 → 4",
        "assumption": "A smaller advantage from withholding creates a coordination game. Trust is an interpretation of expectations, not a measured input.",
        "caption": "Each organization prefers to match the other’s decision. Mutual sharing and mutual non-sharing are both equilibria; neither organization has a dominant strategy.",
        "takeaway": "A cooperative equilibrium can exist alongside a non-cooperative one. This model does not predict which one will be chosen.",
        "matrix": {
            (SHARE, SHARE): (5, 5), (SHARE, PRIVATE): (1, 4),
            (PRIVATE, SHARE): (4, 1), (PRIVATE, PRIVATE): (3, 3),
        },
    },
)


def analyze_scenario(scenario):
    """Calculate all results with the original project's analysis functions."""
    matrix = scenario["matrix"]
    equilibria = {(a, b) for a, b, _ in find_nash_equilibria(matrix)}
    social_optima = {(a, b) for a, b, *_ in find_socially_best_outcome(matrix)}
    outcomes = []
    for index, ((a, b), (pa, pb)) in enumerate(matrix.items()):
        switch_a = PRIVATE if a == SHARE else SHARE
        switch_b = PRIVATE if b == SHARE else SHARE
        next_a = matrix[(switch_a, b)][0]
        next_b = matrix[(a, switch_b)][1]
        outcomes.append({
            "id": f"outcome-{index}", "aStrategy": a, "bStrategy": b,
            "a": pa, "b": pb, "total": pa + pb,
            "isNash": (a, b) in equilibria, "isSocialBest": (a, b) in social_optima,
            "switchA": {"strategy": switch_a, "score": next_a, "gain": next_a - pa},
            "switchB": {"strategy": switch_b, "score": next_b, "gain": next_b - pb},
        })
    return {
        **{key: value for key, value in scenario.items() if key != "matrix"},
        "outcomes": outcomes,
        "dominant": {player: has_dominant_strategy(player, matrix) for player in ("A", "B")},
        "bestResponses": {
            "A": [{"opponent": b, "choices": best_responses_a(b, matrix)} for b in STRATEGIES],
            "B": [{"opponent": a, "choices": best_responses_b(a, matrix)} for a in STRATEGIES],
        },
        "equilibria": [outcome["id"] for outcome in outcomes if outcome["isNash"]],
        "highestTotal": max(outcome["total"] for outcome in outcomes),
    }


def api_payload():
    return {"scenarios": [analyze_scenario(scenario) for scenario in SCENARIOS],
            "analysis": "Pure-strategy Nash equilibria", "source": "Python"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/scenarios":
            try:
                body = json.dumps(api_payload(), ensure_ascii=False).encode("utf-8")
            except Exception:
                self.send_error(500, "Unable to calculate game results")
                return
            self.respond(body, "application/json; charset=utf-8")
            return
        files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/index.html": ("index.html", "text/html; charset=utf-8"),
            "/static/styles.css": ("static/styles.css", "text/css; charset=utf-8"),
            "/static/app.js": ("static/app.js", "text/javascript; charset=utf-8"),
            "/static/favicon.svg": ("static/favicon.svg", "image/svg+xml"),
        }
        if path not in files:
            self.send_error(404, "Page not found")
            return
        filename, content_type = files[path]
        try:
            self.respond((ROOT / filename).read_bytes(), content_type)
        except OSError:
            self.send_error(500, "Website file unavailable")

    def respond(self, body, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="Run the data-sharing dashboard locally.")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as error:
        parser.exit(1, f"Could not start the website: {error}\nTry: python3 server.py --port 8001\n")
    print(f"\n  SHARED INTEREST · Data-sharing game\n  Open http://localhost:{httpd.server_port}\n  Press Ctrl+C to stop.\n", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nWebsite stopped.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
