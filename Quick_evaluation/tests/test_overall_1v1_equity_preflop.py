from pathlib import Path

import pytest

from overall_1v1_equity_preflop import load_overall_equity

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUITED_DIR = PROJECT_ROOT / "Quick_evaluation" / "Suited"
UNSUITED_DIR = PROJECT_ROOT / "Quick_evaluation" / "Unsuited"


@pytest.mark.parametrize(
    "root_dir, rank_a, rank_b, expected",
    [
        (SUITED_DIR, "2", "3", 34.39),
        (UNSUITED_DIR, "3", "2", 30.85),
        (UNSUITED_DIR, "8", "8", 68.96),
    ],
    ids=["suited_2_3", "unsuited_3_2", "pair_8_8"],
)
def test_load_overall_equity(root_dir: Path, rank_a: str, rank_b: str, expected: float) -> None:
    result = load_overall_equity(root_dir, rank_a, rank_b)

    assert result == pytest.approx(expected, abs=0.01)
