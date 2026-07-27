import pytest
import pandas as pd
from pathlib import Path
from quick_eval_1v1 import write_results, load_hand_stats, simulate_hand

BASE_DIR = Path(__file__).resolve().parent
PATH_TO_TEST_FILE = "Fixtures//Test123.csv"

def test_write_results(tmp_path):
    rows = [["Hand", "Wins", "Draws", "Loses"],
            ["6s6d", 1, 2, 3],
            ["AsKh", 3, 2, 1],
            ["Qc6d", 2, 3, 1],
            ["Td2c", 3, 1, 2],
            ["4h4s", 1, 3, 2],
            ["6h8c", 2, 1, 3]]
    path = tmp_path / "File123.csv"
    test_path = PATH_TO_TEST_FILE
    write_results(path, rows)
    df1 = pd.read_csv(path)
    df2 = pd.read_csv(test_path)
    assert df1.equals(df2)

def test_load_hand_stats():
    path = BASE_DIR / PATH_TO_TEST_FILE
    wins, draws, loses = load_hand_stats(path)
    assert wins == draws == loses == 12

def test_simulate_hand_returns_expected_stats_saves_detailed_file():
    hand, wins, draws, loses = simulate_hand("Kc_Ac", write_matchup_csv=True, output_dir=BASE_DIR)
    file = BASE_DIR / "Ac_Kc.csv"

    assert hand == "Kc_Ac"
    assert wins + draws + loses == 1225*1712304 #all opponents times every possible board
    assert wins == 2
    assert draws == 2
    assert loses == 2
    assert file.exists()

def test_simulate_hand_reads_file_if_exists():
    hand, wins, draws, loses = simulate_hand("Qc_Kc", write_matchup_csv=True, output_dir=BASE_DIR / "Fixtures")
    assert wins == draws == loses == 12