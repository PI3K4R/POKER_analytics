from phevaluator.evaluator import evaluate_cards
from itertools import combinations, repeat
from concurrent.futures import ProcessPoolExecutor
import os
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
SUITS = ["c", "d", "h", "s"]
SUITS_MAP = {"c": "\u2663", "d": "\u2666", "h": "\u2665", "s": "\u2660"}

DECK = [f"{RANKS[i]}{SUITS[j]}" for i in range(len(RANKS)) for j in range(len(SUITS))]
START_HANDS_SUITED = [f"{RANKS[i]}c,{RANKS[j]}c" for i in range(len(RANKS)) for j in range(i + 1, len(RANKS))]
START_HANDS_OFFSUIT = [f"{RANKS[i]}c,{RANKS[j]}d" for i in range(len(RANKS)) for j in range(i, len(RANKS))]


def write_results(path: Path, rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def simulate_hand(
    hand: str,
    write_matchup_csv: bool = False,
    output_dir: Path | None = None,
) -> tuple[str, int, int, int]:
    wins = draws = loses = 0
    card1, card2 = hand.split(",")
    hero_cards = (card1, card2)
    game_deck = [c for c in DECK if c not in hero_cards]
    rows = [["Opponent", "Wins", "Draws", "Loses", "Equity%"]] if write_matchup_csv else None

    for op1, op2 in combinations(game_deck, 2):
        remaining = [c for c in game_deck if c not in (op1, op2)]
        wins_op = draws_op = loses_op = 0

        for board in combinations(remaining, 5):
            hero_rank = evaluate_cards(*board, *hero_cards)
            villain_rank = evaluate_cards(*board, op1, op2)

            if hero_rank < villain_rank:
                wins_op += 1
            elif hero_rank > villain_rank:
                loses_op += 1
            else:
                draws_op += 1

        if write_matchup_csv:
            total_op = wins_op + draws_op + loses_op
            rows.append([
                f"{op1}{op2}",
                wins_op,
                draws_op,
                loses_op,
                round((wins_op + 0.5 * draws_op) * 100 / total_op, 2),
            ])

        print("Hand: ", f"{card1}{card2}", "\nVS: ", f"{op1}{op2}", "\nWins: ", wins_op, "\nDraws: ", draws_op, "\nLoses: ", loses_op, "\nEquity%: ", round((wins_op + 0.5 * draws_op) * 100 / total_op, 2))

        wins += wins_op
        draws += draws_op
        loses += loses_op

    if write_matchup_csv and output_dir is not None:
        write_results(output_dir / f"{hand}.csv", rows)

    return hand, wins, draws, loses


if __name__ == "__main__":
    WRITE_MATCHUP_CSV = True
    max_workers = os.cpu_count()
    print("Max workers:", max_workers)

    rows_suited = [["Hand", "Wins", "Draws", "Loses", "Equity%"]]
    rows_offsuit = [["Hand", "Wins", "Draws", "Loses", "Equity%"]]

    suited_dir = BASE_DIR / "Suited"
    offsuit_dir = BASE_DIR / "Offsuit"

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for hand, wins, draws, loses in executor.map(
            simulate_hand,
            START_HANDS_SUITED,
            repeat(WRITE_MATCHUP_CSV),
            repeat(suited_dir),
        ):
            print(hand, "WINS:", wins, "LOSES:", loses, "DRAWS:", draws)
            total = wins + draws + loses
            equity = round((wins + 0.5 * draws) / total * 100, 2)
            rows_suited.append([hand, wins, draws, loses, equity])

        for hand, wins, draws, loses in executor.map(
            simulate_hand,
            START_HANDS_OFFSUIT,
            repeat(WRITE_MATCHUP_CSV),
            repeat(offsuit_dir),
        ):
            print(hand, "WINS:", wins, "LOSES:", loses, "DRAWS:", draws)
            total = wins + draws + loses
            equity = round((wins + 0.5 * draws) / total * 100, 2)
            rows_offsuit.append([hand, wins, draws, loses, equity])

    write_results(suited_dir / "suited_equity.csv", rows_suited)
    write_results(offsuit_dir / "offsuit_equity.csv", rows_offsuit)
