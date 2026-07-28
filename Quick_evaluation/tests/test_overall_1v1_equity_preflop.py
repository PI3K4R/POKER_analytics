from pathlib import Path
import pytest
from overall_1v1_equity_preflop import load_overall_equity, csv_filename, hand_label

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUITED_DIR = PROJECT_ROOT / "Quick_evaluation" / "Suited"
UNSUITED_DIR = PROJECT_ROOT / "Quick_evaluation" / "Unsuited"
RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]


@pytest.mark.parametrize(
    "root_dir, rank_a, rank_b, expected",
    [
        (SUITED_DIR, "2", "3", 34.39),
        (UNSUITED_DIR, "3", "2", 30.85),
        (UNSUITED_DIR, "8", "8", 68.96),
    ],
    ids=["suited_2_3", "unsuited_3_2", "pair_8_8"],
)

def test_csv_filename():
    f1 = csv_filename("2", "3")
    f2 = "3_2.csv"

    assert f1 == f2

def test_load_overall_equity() -> None:
    file = SUITED_DIR / "Q_T.csv"
    result = load_overall_equity(SUITED_DIR, "T", "Q")

    assert file.exists()
    assert result == 2.0

def test_hand_label():
    paired = hand_label("A", "A")
    offsuit = hand_label("K", "T")
    suited = hand_label("T", "K")

    assert paired == "AA"
    assert offsuit == "KTo"
    assert suited == "KTs"
