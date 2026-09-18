from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "latitude",
    "longitude",
    "acquisition_date",
]


def clean_firms_data(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply basic quality-control rules to normalized FIRMS data.
    """

    df = dataframe.copy()

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # ---------------------------------------------------------------
    # Geographic validation
    # ---------------------------------------------------------------

    df = df[
        df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
    ]

    # ---------------------------------------------------------------
    # Remove duplicate detection records.
    # ---------------------------------------------------------------

    duplicate_columns = [
        "latitude",
        "longitude",
        "acquisition_date",
        "acquisition_time",
        "satellite",
        "instrument",
    ]

    available_duplicate_columns = [
        column
        for column in duplicate_columns
        if column in df.columns
    ]

    if available_duplicate_columns:
        df = df.drop_duplicates(
            subset=available_duplicate_columns,
        )

    # ---------------------------------------------------------------
    # Sort chronologically.
    # ---------------------------------------------------------------

    df = df.sort_values(
        [
            "acquisition_date",
            "latitude",
            "longitude",
        ]
    )

    return df.reset_index(drop=True)


def clean_firms_file(
    input_path: str | Path,
    output_path: str | Path,
) -> pd.DataFrame:

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    df = pd.read_parquet(input_path)

    cleaned = clean_firms_data(df)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cleaned.to_parquet(
        output_path,
        index=False,
    )

    return cleaned


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean normalized FIRMS data."
    )

    parser.add_argument(
        "input",
        help="Input normalized FIRMS Parquet",
    )

    parser.add_argument(
        "--output",
        default="data/intermediate/cleaned_firms/firms_clean.parquet",
    )

    args = parser.parse_args()

    cleaned = clean_firms_file(
        args.input,
        args.output,
    )

    print(f"Cleaned records: {len(cleaned)}")
    print(f"Saved to: {args.output}")