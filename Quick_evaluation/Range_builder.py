from random import sample
from typing import Literal

from phevaluator.card import Card
from phevaluator.evaluator import _evaluate_cards


RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
SUITS = ["c", "d", "h", "s"]

POSITIONS_6MAX = {
    "UTG": 5,
    "HJ": 4,
    "CO": 3,
    "BTN": 2,
    "SB": 1,
}

POSITIONS_9MAX = {
    "UTG": 8,
    "UTG+1": 7,
    "UTG+2": 6,
    "LJ": 5,
    "HJ": 4,
    "CO": 3,
    "BTN": 2,
    "SB": 1,
}

DECK_STR = [f"{rank}{suit}" for rank in RANKS for suit in SUITS]
DECK_IDS = [Card.to_id(card) for card in DECK_STR]
RANK_TO_MATRIX_INDEX = {rank: idx for idx, rank in enumerate(RANKS)}


def _build_start_hands() -> list[tuple[str, str]]:
    hands: list[tuple[str, str]] = []
    for i, high_rank in enumerate(RANKS):
        for low_rank in RANKS[i:]:
            if high_rank == low_rank:
                hands.append((f"{high_rank}c", f"{low_rank}d"))
            else:
                hands.append((f"{high_rank}c", f"{low_rank}c"))
                hands.append((f"{high_rank}c", f"{low_rank}d"))
    return hands


START_HANDS = _build_start_hands()


def _simulate_hand_ev(
    hero_card_1: str,
    hero_card_2: str,
    villains_count: int,
    bet_size: float,
    sim_number: int,
) -> dict:
    wins = draws = loses = 0
    hero_ids = (Card.to_id(hero_card_1), Card.to_id(hero_card_2))
    remaining_deck = [card_id for card_id in DECK_IDS if card_id not in hero_ids]
    cards_to_draw = 5 + 2 * villains_count

    for _ in range(sim_number):
        game_cards = sample(remaining_deck, cards_to_draw)
        b0, b1, b2, b3, b4 = game_cards[-5:]
        hero_rank = _evaluate_cards(b0, b1, b2, b3, b4, hero_ids[0], hero_ids[1])
        has_draw = False

        for i in range(0, cards_to_draw - 5, 2):
            villain_rank = _evaluate_cards(
                b0, b1, b2, b3, b4, game_cards[i], game_cards[i + 1]
            )
            if villain_rank < hero_rank:
                loses += 1
                break
            if villain_rank == hero_rank:
                has_draw = True
        else:
            if has_draw:
                draws += 1
            else:
                wins += 1

    total = wins + draws + loses
    win_ratio = wins / total
    lose_ratio = loses / total
    draw_ratio = draws / total
    pot_size = villains_count * bet_size
    ev = win_ratio * pot_size - lose_ratio * bet_size

    return {
        "wins": wins,
        "draws": draws,
        "loses": loses,
        "win_ratio": win_ratio,
        "draw_ratio": draw_ratio,
        "lose_ratio": lose_ratio,
        "ev": ev,
    }


def range_builder(
    game: Literal["6max", "9max"] = "6max",
    position: str = "SB",
    bet_size: float = 2.0,
    pool_size: float = 1.5,
    sim_number: int = 200000,
    threshold: float = -0.05,
) -> dict:
    positions = POSITIONS_6MAX if game == "6max" else POSITIONS_9MAX

    if position not in positions:
        raise ValueError(
            f"Position '{position}' is not valid for {game}. Valid: {list(positions.keys())}"
        )

    villains_count = positions[position]
    ev_matrix: list[list[float | None]] = [[None for _ in RANKS] for _ in RANKS]
    playable_matrix: list[list[bool | None]] = [
        [None for _ in RANKS] for _ in RANKS
    ]
    hand_matrix: list[list[str | None]] = [[None for _ in RANKS] for _ in RANKS]
    by_hand: dict[str, dict] = {}

    for card1, card2 in START_HANDS:
        stats = _simulate_hand_ev(card1, card2, villains_count, bet_size, sim_number)
        hand_key = f"{card1}{card2}"
        is_playable = stats["ev"] >= threshold

        row = RANK_TO_MATRIX_INDEX[card1[0]]
        col = RANK_TO_MATRIX_INDEX[card2[0]]

        # GTO-like layout: suited in upper triangle, offsuit in lower triangle.
        if card1[1] == card2[1]:
            matrix_row, matrix_col = min(row, col), max(row, col)
        else:
            matrix_row, matrix_col = max(row, col), min(row, col)

        by_hand[hand_key] = {
            "hero_cards": [card1, card2],
            "suited": card1[1] == card2[1],
            "ev": stats["ev"],
            "playable": is_playable,
            "wins": stats["wins"],
            "draws": stats["draws"],
            "loses": stats["loses"],
            "win_ratio": stats["win_ratio"],
            "draw_ratio": stats["draw_ratio"],
            "lose_ratio": stats["lose_ratio"],
        }

        ev_matrix[matrix_row][matrix_col] = stats["ev"]
        playable_matrix[matrix_row][matrix_col] = is_playable
        hand_matrix[matrix_row][matrix_col] = hand_key

    return {
        "meta": {
            "game": game,
            "position": position,
            "villains_count": villains_count,
            "bet_size": bet_size,
            "pool_size": pool_size,
            "sim_number": sim_number,
            "threshold": threshold,
        },
        "by_hand": by_hand,
        "heatmap": {
            "labels": RANKS,
            "ev_matrix": ev_matrix,
            "playable_matrix": playable_matrix,
            "hand_matrix": hand_matrix,
        },
    }
