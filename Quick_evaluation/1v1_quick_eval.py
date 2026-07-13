from phevaluator.card import Card
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


def load_hand_stats(path: Path) -> tuple[int, int, int]:
    wins = draws = loses = 0
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            wins += int(row["Wins"])
            draws += int(row["Draws"])
            loses += int(row["Loses"])
    return wins, draws, loses


def simulate_hand(
    hand: str,
    write_matchup_csv: bool = False,
    output_dir: Path | None = None,
) -> tuple[str, int, int, int]:
    if write_matchup_csv and output_dir is not None:
        output_path = output_dir / f"{hand}.csv"
        if output_path.exists():
            wins, draws, loses = load_hand_stats(output_path)
            return hand, wins, draws, loses

    wins = draws = loses = 0
    card1, card2 = hand.split(",")
    hero_cards = (card1, card2)
    game_deck = [c for c in DECK if c not in hero_cards]
    hero_ids = (Card.to_id(card1), Card.to_id(card2))
    deck_ids = [Card.to_id(c) for c in game_deck]

    rows = [["Opponent", "Wins", "Draws", "Loses", "Equity%"]] if write_matchup_csv else None

    if card1[1] == card2[1]:
        card1 = card1[0] + "c"
        card2 = card2[0] + "c"
        suited_sm = [Card.to_id(c) for c in game_deck if c[1] == "c"]
        suited_diff = [Card.to_id(c) for c in game_deck if c[1] == "d"]

        suited_vs_1offsuit = [(c1, c2) for c1 in suited_sm for c2 in suited_diff]
        suited_vs_2offsuit = []
        seen = set()
        for c1 in game_deck:
            if c1[1] != "d":
                continue
            for c2 in game_deck:
                if c2[1] != "h":
                    continue

                values = tuple(sorted((c1[0], c2[0]), key=lambda x: ord(x)))
                if values not in seen:
                    seen.add(values)
                    suited_vs_2offsuit.append((Card.to_id(c1), Card.to_id(c2)))
        suited_vs_suited_diff = combinations(suited_diff, 2)
        suited_vs_suited_sm = combinations(suited_sm, 2)

        list_of_opps = [(suited_vs_1offsuit, 3), (suited_vs_2offsuit, 'mark_s'), (suited_vs_suited_diff, 3), (suited_vs_suited_sm, 1)]

    else:
        card1 = card1[0] + "c"
        card2 = card2[0] + "d"
        suited_sm = [Card.to_id(c) for c in game_deck if c[1] == "c"]
        suited_diff = [Card.to_id(c) for c in game_deck if c[1] == "h"]

        suited_vs_1offsuit = combinations(suited_sm, 2)
        offsuit_vs_1offsuit = [(c1, c2) for c1 in suited_sm for c2 in suited_diff]
        suited_vs_2offsuit = combinations(suited_diff, 2)
        offsuit_vs_2offsuit_diff = []
        seen = set()
        for c1 in game_deck:
            if c1[1] != "h":
                continue
            for c2 in game_deck:
                if c2[1] != "s":
                    continue

                values = tuple(sorted((c1[0], c2[0]), key=lambda x: ord(x)))
                if values not in seen:
                    seen.add(values)
                    offsuit_vs_2offsuit_diff.append((Card.to_id(c1), Card.to_id(c2)))
        offsuit_vs_2offsuit_sm = [(Card.to_id(c1), Card.to_id(c2)) for c1 in game_deck if c1[1] == "c" for c2 in game_deck if c2[1] == "d"]

        list_of_opps = [(suited_vs_1offsuit, 2), (offsuit_vs_1offsuit, 4), (suited_vs_2offsuit, 2), (offsuit_vs_2offsuit_diff, 'mark_o'), (offsuit_vs_2offsuit_sm, 1)]

    for opponents in list_of_opps:
        for op1, op2 in opponents[0]:
            if opponents[1] == 'mark_s':
                multiplier = 3 if op1 // 4 == op2 // 4 else 6
            elif opponents[1] == 'mark_o':
                multiplier = 1 if op1 // 4 == op2 // 4 else 2
            else:
                multiplier = opponents[1]

            remaining = [c for c in deck_ids if c not in (op1, op2)]
            wins_op = draws_op = loses_op = 0

            for board in combinations(remaining, 5):
                hero_rank = evaluate_cards(*board, *hero_ids)
                villain_rank = evaluate_cards(*board, op1, op2)

                if hero_rank < villain_rank:
                    wins_op += multiplier
                elif hero_rank > villain_rank:
                    loses_op += multiplier
                else:
                    draws_op += multiplier

            if write_matchup_csv:
                total_op = wins_op + draws_op + loses_op
                rows.append([
                    f"{Card(op1).describe_card()}{Card(op2).describe_card()}",
                    wins_op,
                    draws_op,
                    loses_op,
                    round((wins_op + 0.5 * draws_op) * 100 / total_op, 2),
                ])
                print(
                    "Hero vs Villain:",
                    f"{card1}{card2}_vs_{Card(op1).describe_card()}{Card(op2).describe_card()}",
                    "\nWins:", wins_op,
                    "\nDraws:", draws_op,
                    "\nLoses:", loses_op,
                    "\nEquity_%:", round((wins_op + 0.5 * draws_op) * 100 / total_op, 2),
                )

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
