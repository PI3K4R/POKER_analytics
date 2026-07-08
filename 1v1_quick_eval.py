from phevaluator.evaluator import evaluate_cards
from itertools import combinations
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

def simulate_hand(hand: str) -> tuple[str, int, int, int]:
    wins = draws = loses = 0
    card1, card2 = hand.split(",")
    hero_cards = (card1, card2)
    game_deck = [c for c in DECK if c not in hero_cards]

    for op1, op2 in combinations(game_deck, 2):
        remaining = [c for c in game_deck if c not in (op1, op2)]

        for board in combinations(remaining, 5):
            hero_rank = evaluate_cards(*board, *hero_cards)
            villain_rank = evaluate_cards(*board, op1, op2)

            if hero_rank < villain_rank:
                wins += 1

            elif hero_rank > villain_rank:
                loses += 1

            else:
                draws += 1

    return hand, wins, draws, loses


if __name__ == '__main__':
    max_workers = os.cpu_count() or 4
    print("Max workers: ", max_workers)
    rows_suited = [["Hand", "Wins", "Draws", "Loses", "Equity%"]]
    rows_offsuit = [["Hand", "Wins", "Draws", "Loses", "Equity%"]]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for hand, wins, draws, loses in executor.map(simulate_hand, START_HANDS_SUITED):
            print(hand, "WINS:", wins, "LOSES:", loses, "DRAWS:", draws)
            total = wins + draws + loses
            equity = round((wins + 0.5 * draws) / total * 100, 2)
            rows_suited.append([hand, wins, draws, loses, equity])

        for hand, wins, draws, loses in executor.map(simulate_hand, START_HANDS_OFFSUIT):
            print(hand, "WINS:", wins, "LOSES:", loses, "DRAWS:", draws)
            total = wins + draws + loses
            equity = round((wins + 0.5 * draws) / total * 100, 2)
            rows_offsuit.append([hand, wins, draws, loses, equity])

    write_results(BASE_DIR / "suited_equity.csv", rows_suited)
    write_results(BASE_DIR / "offsuit_equity.csv", rows_offsuit)