from pathlib import Path
import runpy


if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "User-friendly_evaluation" / "hands_winning_data_csv.py"
    runpy.run_path(str(target), run_name="__main__")
