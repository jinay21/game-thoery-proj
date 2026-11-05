# Shared Interest — Data-Sharing Game

A localhost website for presenting **Game-Theoretic Analysis of Data Sharing Between Competing Organizations**. The interface uses HTML, CSS, and JavaScript. Python calculates payoffs, best responses, strictly dominant strategies, pure-strategy Nash equilibria, and the highest combined utility.

## Start the website

Requires Python 3.9 or later. No package installation is needed.

Open a terminal in this folder and run:

```bash
python3 server.py
```

Open **http://localhost:8000** in your browser. Keep the terminal open while presenting; press Ctrl+C to stop the server. Do not open `index.html` directly: the page needs the Python API. Google Fonts improves typography when internet is available; system fonts provide a fallback.

If port 8000 is already occupied:

```bash
python3 server.py --port 8001
```

Then open **http://localhost:8001**. The server accepts connections from this computer only.

## Suggested presentation (3–5 minutes)

1. Start with **The project, in brief**: two organizations choose whether to share; each payoff depends on both decisions. Scores are illustrative utility, not money or empirical company data.
2. **Competitive environment**: begin at Share / Share, earning (5, 5). Show that either organization could switch alone and earn 7. Choose Don’t Share for both: (3, 3) is stable, even though the combined score drops from 10 to 6.
3. **Sharing incentive**: each sharing organization receives an assumed bonus of 3. Share / Share now gives (8, 8); switching alone lowers a player’s score to 7. Sharing is dominant for both. The model excludes any external cost of providing the bonus.
4. **Trust-dependent cooperation**: the one-sided withholding score falls from 7 to 4. Show both Share / Share and Don’t Share / Don’t Share. Both are pure-strategy Nash equilibria. Try either mismatched outcome to show why it is unstable. There is no dominant strategy. Expectations matter, but trust is not a measured variable and the model does not select one equilibrium.
5. End at the comparison table: changing incentives changes stable outcomes. Use the visible presentation cues and unilateral-switch captions throughout.

## Features

- Three fixed scenarios; no payoff editing.
- Click matrix cells or decision buttons to select all four outcomes.
- Distinct badges for Nash equilibria and the highest combined score.
- Individual and combined scores, unilateral-switch explanations, dominant strategies, best responses, chart, comparison table, and concept definitions.
- Keyboard-accessible controls, screen-reader updates, responsive layout, reduced-motion support, and a connection error with retry.
- All results come from Python through `GET /api/scenarios`; frontend selection does not alter payoff values.

## Project files

- `server.py`: local server, scenario definitions, analysis API.
- `data_sharing_game.py`: original Python project, extended to accept optional payoff matrices without changing the baseline command-line output. The original download is untouched.
- `index.html`, `static/styles.css`, `static/app.js`: dashboard and interactions.
- `test_analysis.py`: calculation and HTTP integration checks.

The original analysis is still available with `python3 data_sharing_game.py`. Its optional `--plot` flag requires matplotlib; the website itself does not.

## Run checks

```bash
python3 -B -m unittest -v test_analysis.py
```

## Model boundaries

This is a two-player, simultaneous, one-shot game with two actions. The website reports **pure-strategy** equilibria only; mixed equilibria and repeated-game behavior are outside its scope. The third scenario also admits a mixed-strategy equilibrium, which is not analyzed by this project. Combining utilities is a modeling convention, not a measurement of net economic welfare. Reports and slides have not been revised for these extensions.
