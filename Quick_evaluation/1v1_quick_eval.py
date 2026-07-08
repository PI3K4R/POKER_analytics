from phevaluator.evaluator import evaluate_cards
from itertools import combinations, repeat
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RANKS = [2, 3, 4, 5, 6, 7, 8, 9, "T", "J", "Q", "K", "A"]
SUITS = ["c", "d", "h", "s"]
SUITS_MAP = {"c": "\u2663", "d": "\u2666", "h": "\u2665", "s": "\u2660"}

DECK = [f"{RANKS[i]}{SUITS[j]}" for i in range(len(RANKS)) for j in range(len(SUITS))]
START_HANDS_SUITED = [f"{RANKS[i]}c,{RANKS[j]}c" for i in range(len(RANKS)) for j in range(i + 1, len(RANKS))]
START_HANDS_OFFSUIT = [f"{RANKS[i]}c,{RANKS[j]}d" for i in range(len(RANKS)) for j in range(i, len(RANKS))]


def write_results(path: Path, rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

def simulate_hand(hand: str, WRITE_MATCHUP_CSV: bool = False) -> tuple[str, int, int, int]:
    wins = draws = loses = 0
    card1, card2 = hand.split(",")
    hero_cards = (card1, card2)
    game_deck = [c for c in DECK if c not in hero_cards]

    if WRITE_MATCHUP_CSV:
        rows = [["Opponent", "Wins", "Draws", "Loses", "Equity%"]]

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

        if WRITE_MATCHUP_CSV:
            total = wins_op + draws_op + loses_op
            rows.append([f"{op1}{op2}", wins_op, draws_op, loses_op, round((wins_op + 0.5 * draws_op)*100 / total, 2)])

        wins += wins_op
        draws += draws_op
        loses += loses_op
        print("KUPAGOWNOCHUUUUJ")
    return hand, wins, draws, loses


if __name__ == '__main__':
    max_workers = os.cpu_count() - 4 or 4
    print("Max workers: ", max_workers)
    rows_suited = [["Hand", "Wins", "Draws", "Loses", "Equity%"]]
    rows_offsuit = [["Hand", "Wins", "Draws", "Loses", "Equity%"]]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for hand, wins, draws, loses in executor.map(simulate_hand, START_HANDS_SUITED, repeat(True)):
            print(hand, "WINS:", wins, "LOSES:", loses, "DRAWS:", draws)
            write_results(BASE_DIR / f"Suited/{hand}.csv", rows)
            total = wins + draws + loses
            equity = round((wins + 0.5 * draws) / total * 100, 2)
            rows_suited.append([hand, wins, draws, loses, equity])

        for hand, wins, draws, loses in executor.map(simulate_hand, START_HANDS_OFFSUIT, repeat(True)):
            print(hand, "WINS:", wins, "LOSES:", loses, "DRAWS:", draws)
            write_results(BASE_DIR / f"Offsuit/{hand}.csv", rows)
            total = wins + draws + loses
            equity = round((wins + 0.5 * draws) / total * 100, 2)
            rows_offsuit.append([hand, wins, draws, loses, equity])

    write_results(BASE_DIR / "Suited/suited_equity.csv", rows_suited)
    write_results(BASE_DIR / "Offsuit/offsuit_equity.csv", rows_offsuit)