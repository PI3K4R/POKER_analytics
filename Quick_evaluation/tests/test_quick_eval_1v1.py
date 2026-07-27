import pytest
import pandas as pd
from pathlib import Path
from quick_eval_1v1 import write_results, load_hand_stats, simulate_hand

BASE_DIR = Path(__file__).resolve().parent
PATH_TO_NEW_FILE = "File123.csv"
PATH_TO_TEST_FILE = "Fixtures//Test123.csv"
DECK = [f"{rank}{suit}" for rank in RANKS for suit in SUITS]

def test_write_results():
    rows = [["Hand", "Wins", "Draws", "Loses"],
            ["6s6d", 1, 2, 3],
            ["AsKh", 3, 2, 1],
            ["Qc6d", 2, 3, 1],
            ["Td2c", 3, 1, 2],
            ["4h4s", 1, 3, 2],
            ["6h8c", 2, 1, 3]]
    path = PATH_TO_NEW_FILE
    test_path = PATH_TO_TEST_FILE
    write_results(path, rows)
    df1 = pd.read_csv(path)
    df2 = pd.read_csv(test_path)
    assert df1 == df2

def test_load_hand_stats():
    path = BASE_DIR / PATH_TO_TEST_FILE
    wins, draws, loses = load_hand_stats(path)
    assert wins == draws == loses == 12

def test_simulate_hand_returns_expected_stats():
    hand, wins, draws, loses = simulate_hand("Ac,Kc")

    assert hand == "Ac,Kc"
    assert wins == pass
    assert draws == pass
    assert loses == pass

