from pathlib import Path
import runpy


if __name__ == "__main__":
    target = Path(__file__).resolve().parent / "Quick_evaluation" / "1v1_quick_eval.py"
    runpy.run_path(str(target), run_name="__main__")
