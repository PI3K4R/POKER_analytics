import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR_SUITED = BASE_DIR / "Suited"
ROOT_DIR_UNSUITED = BASE_DIR / "Unsuited"


def csv_filename(rank_a: str, rank_b: str) -> str:
    """
    param rank_a: Rank of a first card
    param rank_b: Rank of a second card

    Returns csv files names accordingly to naming convention ("{rank_a}{suit}_{rank_b}{suit}.csv") where rank_a >= rank_b
    """
    high_idx, low_idx = sorted([RANKS.index(r) for r in (rank_a, rank_b)], reverse=True)
    return f"{RANKS[high_idx]}_{RANKS[low_idx]}.csv"


def load_overall_equity(root_dir: Path, rank_a: str, rank_b: str) -> float | None:
    """
    From existing files with evaluation of hand: rank_a, rank_b (suited or not) this function gets it's number of wins, draws and loses
    :param root_dir: Suited or offsuit catalog
    :param rank_a: Rank of first card in hand
    :param rank_b: Rank of second card in hand
    :return: Equity with formula: (sum_wins + 0.5*sum_draws) / (sum_wins + sum_loses + sum_draws) * 100
    """
    filename = csv_filename(rank_a, rank_b)
    sum_wins = 0.0
    sum_draws = 0.0
    sum_loses = 0.0
    found = False

    for root, _, files in os.walk(root_dir):
        if "Sorted_equity" in root or filename not in files:
            continue

        found = True
        df = pd.read_csv(Path(root) / filename)
        sum_wins += df["Wins"].sum()
        sum_draws += df["Draws"].sum()
        sum_loses += df["Loses"].sum()

    if not found or sum_wins + sum_loses == 0:
        return None
    return (sum_wins + 0.5*sum_draws) / (sum_wins + sum_loses + sum_draws) * 100


def hand_label(row_rank: str, col_rank: str) -> str:
    """
    Function which gets starting hand based on it's position in a grid
    :param row_rank: Row index in a grid
    :param col_rank: Column index in a grid
    :return: Starting hand with 's' or 'o' (depends on a suits) in format '{rank1}{rank2}{suffix}'
    """

    if row_rank == col_rank:
        return f"{row_rank}{col_rank}"

    high, low, suffix = (
        (row_rank, col_rank, "o")
        if RANKS.index(row_rank) > RANKS.index(col_rank)
        else (col_rank, row_rank, "s")
    )

    return f"{high}{low}{suffix}"


def build_gto_equity_grid() -> tuple[np.ndarray, np.ndarray]:
    """
    :return: Building raw Poker grid with equity for all hands (suited and offsuit)
    """
    grid = np.full((len(RANKS), len(RANKS)), np.nan)
    labels = np.empty((len(RANKS), len(RANKS)), dtype=object)

    for row_idx, row_rank in enumerate(RANKS):
        for col_idx, col_rank in enumerate(RANKS):
            labels[row_idx, col_idx] = hand_label(row_rank, col_rank)

            if row_idx < col_idx:
                root_dir = ROOT_DIR_SUITED
            else:
                root_dir = ROOT_DIR_UNSUITED

            grid[row_idx, col_idx] = load_overall_equity(root_dir, row_rank, col_rank)

    return grid, labels


def plot_gto_equity_grid(grid: np.ndarray, labels: np.ndarray) -> None:
    """
    :param grid: Numpy matrix with equities for all starting hands accordingly to standard Poker grids (suited pairs on a upper triangle of the matrix)
    :param labels: Poker ranks in descending order to it's power
    :return: Display and save Poker grid with 1v1 equities for all starting hands
    """
    annot = np.empty_like(labels, dtype=object)
    for row_idx in range(len(RANKS)):
        for col_idx in range(len(RANKS)):
            value = grid[row_idx, col_idx]
            if np.isnan(value):
                annot[row_idx, col_idx] = labels[row_idx, col_idx]
            else:
                annot[row_idx, col_idx] = f"{labels[row_idx, col_idx]}\n{value:.1f}"

    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(
        grid,
        ax=ax,
        cmap="viridis",
        xticklabels=RANKS,
        yticklabels=RANKS,
        square=True,
        annot=annot,
        fmt="",
        cbar_kws={"label": "Overall Equity (%)"},
        linewidths=0.5,
        linecolor="white",
    )

    ax.set_title("1v1 Preflop Overall Equity (GTO grid)")
    ax.set_xlabel("Second card")
    ax.set_ylabel("First card")
    ax.tick_params(axis="both", labelsize=11)

    plt.tight_layout()
    plt.savefig("Overall_equity_GTO_grid.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    equity_grid, hand_labels = build_gto_equity_grid()
    plot_gto_equity_grid(equity_grid, hand_labels)
