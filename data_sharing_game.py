"""
Game-Theoretic Analysis of Data Sharing Between Competing Organizations
A small, self-contained Python project using a 2-player normal-form game.

Run:
    python3 data_sharing_game.py

Optional payoff plot:
    python3 data_sharing_game.py --plot
    (requires matplotlib)

Payoffs are illustrative utility scores, not real monetary values.
"""

from itertools import product
import argparse

STRATEGIES = ("Share", "Don't Share")

# PAYOFFS[(A strategy, B strategy)] = (A utility, B utility)
PAYOFFS = {
    ("Share", "Share"): (5, 5),
    ("Share", "Don't Share"): (1, 7),
    ("Don't Share", "Share"): (7, 1),
    ("Don't Share", "Don't Share"): (3, 3),
}


def payoff(a_strategy, b_strategy, payoffs=None):
    """Return (A's payoff, B's payoff) for a strategy pair."""
    return (PAYOFFS if payoffs is None else payoffs)[(a_strategy, b_strategy)]


def best_responses_a(b_strategy, payoffs=None):
    """Return A's strategy/strategies with the highest payoff against B."""
    values = {a: payoff(a, b_strategy, payoffs)[0] for a in STRATEGIES}
    best = max(values.values())
    return [a for a, value in values.items() if value == best]


def best_responses_b(a_strategy, payoffs=None):
    """Return B's strategy/strategies with the highest payoff against A."""
    values = {b: payoff(a_strategy, b, payoffs)[1] for b in STRATEGIES}
    best = max(values.values())
    return [b for b, value in values.items() if value == best]


def find_nash_equilibria(payoffs=None):
    """A strategy pair is Nash if neither player can improve unilaterally."""
    equilibria = []
    for a, b in product(STRATEGIES, repeat=2):
        if a in best_responses_a(b, payoffs) and b in best_responses_b(a, payoffs):
            equilibria.append((a, b, payoff(a, b, payoffs)))
    return equilibria


def find_socially_best_outcome(payoffs=None):
    """Maximize the sum of both players' payoffs (social welfare)."""
    outcomes = []
    matrix = PAYOFFS if payoffs is None else payoffs
    highest_total = max(sum(p) for p in matrix.values())
    for (a, b), (pa, pb) in matrix.items():
        if pa + pb == highest_total:
            outcomes.append((a, b, pa, pb, pa + pb))
    return outcomes


def has_dominant_strategy(player, payoffs=None):
    """Find a strategy that gives the player a strictly higher payoff
    against every strategy of the other player. Return None if absent.
    """
    if player == "A":
        for candidate in STRATEGIES:
            if all(
                payoff(candidate, other, payoffs)[0] > payoff(alternative, other, payoffs)[0]
                for other in STRATEGIES
                for alternative in STRATEGIES
                if alternative != candidate
            ):
                return candidate
    elif player == "B":
        for candidate in STRATEGIES:
            if all(
                payoff(other, candidate, payoffs)[1] > payoff(other, alternative, payoffs)[1]
                for other in STRATEGIES
                for alternative in STRATEGIES
                if alternative != candidate
            ):
                return candidate
    else:
        raise ValueError("player must be 'A' or 'B'")
    return None


def print_payoff_matrix():
    """Print a readable payoff matrix."""
    print("\nPAYOFF MATRIX (A's payoff, B's payoff)")
    print("-" * 61)
    print(f"{'Organization A / B':<25}{'B: Share':>17}{'B: Don’t Share':>19}")
    print("-" * 61)
    for a in STRATEGIES:
        left = f"A: {a}"
        p_share = payoff(a, "Share")
        p_private = payoff(a, "Don't Share")
        print(f"{left:<25}{str(p_share):>17}{str(p_private):>19}")
    print("-" * 61)


def run_analysis():
    print("=" * 66)
    print("GAME-THEORETIC ANALYSIS OF DATA SHARING")
    print("=" * 66)
    print("Players: Organization A and Organization B")
    print("Strategies: Share data / Don't share data")
    print("Payoffs are illustrative utility scores.")
    print_payoff_matrix()

    print("\nBEST RESPONSES")
    for b in STRATEGIES:
        print(f"If B chooses '{b}', A's best response(s): {best_responses_a(b)}")
    for a in STRATEGIES:
        print(f"If A chooses '{a}', B's best response(s): {best_responses_b(a)}")

    print("\nDOMINANT STRATEGIES")
    print(f"Organization A: {has_dominant_strategy('A') or 'No strictly dominant strategy'}")
    print(f"Organization B: {has_dominant_strategy('B') or 'No strictly dominant strategy'}")

    print("\nNASH EQUILIBRIUM")
    equilibria = find_nash_equilibria()
    if equilibria:
        for a, b, (pa, pb) in equilibria:
            print(f"({a}, {b}) -> payoffs ({pa}, {pb})")
        print("At this outcome, neither organization can improve its payoff by changing")
        print("its own strategy alone while the other organization's strategy stays fixed.")
    else:
        print("No pure-strategy Nash equilibrium found.")

    print("\nSOCIAL WELFARE")
    for a, b, pa, pb, total in find_socially_best_outcome():
        print(f"Highest combined payoff: ({a}, {b}) -> ({pa}, {pb}); total = {total}")
    print("This is the outcome with the highest sum of payoffs, not necessarily the")
    print("outcome that each organization chooses individually.")

    print("\nINTERPRETATION")
    print("- Each organization individually prefers not to share, given either action")
    print("  by the other organization.")
    print("- Therefore, mutual non-sharing is the Nash equilibrium in this model.")
    print("- Mutual sharing gives a higher combined payoff (10 versus 6), illustrating")
    print("  a conflict between individual incentives and collective benefit.")
    print("- In practice, contracts, trusted intermediaries, privacy controls, and")
    print("  repeated cooperation may change the payoff structure.")


def plot_payoffs():
    """Create a payoff heatmap, if matplotlib is installed."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Plot unavailable: install matplotlib with 'python3 -m pip install matplotlib'")
        return

    labels = ["Share", "Don't Share"]
    a_values = [[payoff(a, b)[0] for b in STRATEGIES] for a in STRATEGIES]
    b_values = [[payoff(a, b)[1] for b in STRATEGIES] for a in STRATEGIES]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, values, title, player in [
        (axes[0], a_values, "Organization A payoff", "A"),
        (axes[1], b_values, "Organization B payoff", "B"),
    ]:
        im = ax.imshow(values, cmap="Blues", vmin=0, vmax=7)
        ax.set_xticks(range(2), labels=["B: Share", "B: Don't Share"])
        ax.set_yticks(range(2), labels=["A: Share", "A: Don't Share"])
        ax.set_title(title)
        ax.set_xlabel("Organization B strategy")
        ax.set_ylabel("Organization A strategy")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(values[i][j]), ha="center", va="center",
                        color="black", fontsize=14, fontweight="bold")
    fig.suptitle("Illustrative utility scores for data-sharing decisions")
    fig.tight_layout()
    output = "payoff_heatmap.png"
    fig.savefig(output, dpi=180, bbox_inches="tight")
    print(f"Saved payoff heatmap to {output}")
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Analyze a data-sharing game.")
    parser.add_argument("--plot", action="store_true", help="show and save payoff heatmap")
    args = parser.parse_args()
    run_analysis()
    if args.plot:
        plot_payoffs()


if __name__ == "__main__":
    main()
