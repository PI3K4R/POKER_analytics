import os
from pathlib import Path

import pandas as pd

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIRS = [BASE_DIR / "Suited", BASE_DIR / "Unsuited"]

DISPLAY_COLUMNS = ["vs_Hand", "type", "Equity_%", "Draws_%", "Loses_%"]
PERCENT_COLUMNS = ["Equity_%", "Draws_%", "Loses_%"]


def aggregate_hand_data(root_dir: Path, rank_low: str, rank_high: str) -> pd.DataFrame:
    filename = f"{rank_low}_{rank_high}.csv"
    frames: list[pd.DataFrame] = []

    for current_root, _, files in os.walk(root_dir):
        if "Sorted_equity" in current_root or filename not in files:
            continue

        frames.append(pd.read_csv(Path(current_root) / filename))

    if not frames:
        return pd.DataFrame(columns=DISPLAY_COLUMNS)

    combined = pd.concat(frames, ignore_index=True)
    combined["Wins"] = combined.filter(like="Wins").sum(axis=1)

    total = combined["Wins"] + combined["Draws"] + combined["Loses"]
    combined["Equity_%"] = (combined["Wins"] / total * 100).round(2)
    combined["Draws_%"] = (combined["Draws"] / total * 100).round(2)
    combined["Loses_%"] = (combined["Loses"] / total * 100).round(2)

    return (
        combined[DISPLAY_COLUMNS]
        .sort_values("Equity_%", ascending=False)
        .reset_index(drop=True)
    )


def generate_sorted_equity_csv(root_dir: Path, include_pairs: bool) -> list[Path]:
    output_dir = root_dir / "Sorted_equity"
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files: list[Path] = []
    start_offset = 0 if include_pairs else 1

    for rank_low in RANKS:
        for rank_high in RANKS[RANKS.index(rank_low) + start_offset :]:
            aggregated = aggregate_hand_data(root_dir, rank_low, rank_high)
            if aggregated.empty:
                continue

            csv_path = output_dir / f"{rank_low}_{rank_high}.csv"
            aggregated.to_csv(csv_path, index=True)
            generated_files.append(csv_path)

    return generated_files


def generate_sorted_equity_csvs() -> list[Path]:
    generated_files: list[Path] = []
    generated_files.extend(generate_sorted_equity_csv(BASE_DIR / "Suited", include_pairs=False))
    generated_files.extend(generate_sorted_equity_csv(BASE_DIR / "Unsuited", include_pairs=True))
    return generated_files


def build_html_table(df: pd.DataFrame, caption: str):
    table_df = df[DISPLAY_COLUMNS].copy()

    if "Equity_%" in table_df.columns:
        table_df = table_df.sort_values("Equity_%", ascending=False).reset_index(drop=True)

    styler = table_df.style.set_caption(caption).format(
        {column: "{:.2f}" for column in PERCENT_COLUMNS}
    )
    return styler.background_gradient(subset=["Equity_%"], cmap="Blues")


def generate_html_for_csv(csv_path: Path) -> Path:
    df = pd.read_csv(csv_path)
    html_path = csv_path.with_suffix(".html")
    build_html_table(df, caption=csv_path.stem).to_html(html_path)
    return html_path


def generate_sorted_equity_html() -> list[Path]:
    generated_files: list[Path] = []

    for root_dir in ROOT_DIRS:
        sorted_equity_dir = root_dir / "Sorted_equity"
        if not sorted_equity_dir.is_dir():
            continue

        for csv_path in sorted(sorted_equity_dir.glob("*.csv")):
            generated_files.append(generate_html_for_csv(csv_path))

    return generated_files


if __name__ == "__main__":

    csv_files = generate_sorted_equity_csvs()
    print(f"Wygenerowano {len(csv_files)} plikow CSV w Sorted_equity.")

    html_files = generate_sorted_equity_html()
    print(f"Wygenerowano {len(html_files)} plikow HTML w Sorted_equity.")

    for root_dir in ROOT_DIRS:
        sorted_equity_dir = root_dir / "Sorted_equity"
        if not sorted_equity_dir.is_dir():
            continue
