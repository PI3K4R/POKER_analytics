from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

from Quick_evaluation.Range_builder import (
    _build_start_hands,
    _gto_hand_label,
    _simulate_hand_ev,
    draw_playable_grid,
    range_builder,
)

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
SUITS = ["c", "d", "h", "s"]

def test__build_start_hands():
    start_hands = set(_build_start_hands())
    pairs = [h for h in start_hands if h[0][0] == h[1][0]]
    suited = [h for h in start_hands if h[0][1] == h[1][1]]
    offsuit = [h for h in start_hands if h[0][1] != h[1][1] and h not in pairs]

    assert len(pairs) == 13
    assert len(suited) == 78
    assert len(offsuit) == 78
    assert len(start_hands) == 169

    for el in start_hands:
        assert (el[0][0] in RANKS and el[1][0] in RANKS)
        assert (el[0][1] == 'c' and (el[1][1] == 'c' or el[1][1] == 'd'))


def test__simulate_hand_ev():
    simulation = _simulate_hand_ev("8c", "7h", 4, 1.5, 100)
    all_iterations = simulation["wins"] + simulation["draws"] + simulation["loses"]

    assert all_iterations == 100
    assert simulation["win_ratio"] == simulation["wins"] / all_iterations
    assert simulation["draw_ratio"] == simulation["draws"] / all_iterations
    assert simulation["lose_ratio"] == simulation["loses"] / all_iterations
    assert simulation["ev"] == 6*simulation["win_ratio"] - 1.5*simulation["lose_ratio"]


def test_range_builder():
    test_range = range_builder("6max", "CO", 1.5, 1.5, 100, 0)

    assert test_range["meta"]["game"] == "6max"
    assert test_range["meta"]["position"] == "CO"
    assert test_range["meta"]["villains_count"] == 3
    assert test_range["meta"]["bet_size"] == test_range["meta"]["pool_size"] == 1.5
    assert test_range["meta"]["sim_number"] == 100
    assert test_range["meta"]["threshold"] == 0.0
    assert len(test_range["by_hand"]) == 169

    for key, item in test_range["by_hand"].items():
        assert item["hero_cards"] == [key[:2], key[2:]]
        if key[1] == key[3]:
            assert item["suited"] is True
        else:
            assert item["suited"] is False

        assert item["playable"] is (item["ev"] >= test_range["meta"]["threshold"])

    assert test_range["heatmap"]["labels"] == RANKS
    assert len(test_range["heatmap"]["ev_matrix"]) == len(test_range["heatmap"]["playable_matrix"]) == 13

    for el in test_range["heatmap"]["ev_matrix"]:
        assert len(el) == 13

    for el in test_range["heatmap"]["playable_matrix"]:
        assert len(el) == 13


def _fake_range_builder_obj() -> dict:
    playable_matrix = []
    ev_matrix = []
    for row in range(len(RANKS)):
        playable_row = []
        ev_row = []
        for col in range(len(RANKS)):
            is_playable = row + col <= 8
            playable_row.append(is_playable)
            ev_row.append(0.5 if is_playable else -0.4)
        playable_matrix.append(playable_row)
        ev_matrix.append(ev_row)

    return {
        "meta": {
            "game": "6max",
            "position": "CO",
            "villains_count": 3,
            "bet_size": 1.5,
            "pool_size": 1.5,
            "sim_number": 100,
            "threshold": 0.0,
        },
        "by_hand": {},
        "heatmap": {
            "labels": RANKS,
            "ev_matrix": ev_matrix,
            "playable_matrix": playable_matrix,
        },
    }


def test_gto_hand_label():
    assert _gto_hand_label("A", "A") == "AA"
    assert _gto_hand_label("A", "K") == "AKs"
    assert _gto_hand_label("K", "A") == "AKo"
    assert _gto_hand_label("K", "T") == "KTs"
    assert _gto_hand_label("T", "K") == "KTo"


def test_draw_playable_grid(tmp_path: Path):
    output = draw_playable_grid(_fake_range_builder_obj(), output_dir=tmp_path)

    assert output.exists()
    assert output.parent == tmp_path
    assert output.name == "6max_CO_bet1.5_thr0.0bb_playable_grid.png"
    assert output.stat().st_size > 0


def test_draw_playable_grid_rejects_invalid_object(tmp_path: Path):
    with pytest.raises(ValueError):
        draw_playable_grid({"meta": {}}, output_dir=tmp_path)