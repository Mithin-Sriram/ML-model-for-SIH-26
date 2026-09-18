from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


# ---------------------------------------------------------------------
# Standard column names used by our project
# ---------------------------------------------------------------------

COLUMN_ALIASES = {
    "latitude": [
        "latitude",
        "lat",
    ],
    "longitude": [
        "longitude",
        "lon",
        "long",
    ],
    "frp": [
        "frp",
        "frp_mw",
    ],
    "brightness": [
        "bright_ti4",
        "brightness_temp_i4_k",
        "brightness",
        "bright_t31",
    ],
    "brightness_i5": [
        "bright_ti5",
        "brightness_temp_i5_k",
    ],
    "confidence": [
        "confidence",
        "confidence_pct",
    ],
    "day_night": [
        "daynight",
        "day_night_flag",
        "day_night",
    ],
    "acquisition_date": [
        "acq_date",
        "acquisition_date",
    ],
    "acquisition_time": [
        "acq_time",
        "acquisition_time",
    ],
    "satellite": [
        "satellite",
    ],
    "instrument": [
        "instrument",
    ],
]


def _find_column(
    dataframe: pd.DataFrame,
    candidates: list[str],
) -> Optional[str]:
    """
    Find the first matching column from a list of possible aliases.
    Matching is case-insensitive.
    """

    normalized = {
        str(column).strip().lower(): column
        for column in dataframe.columns
    }

    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]

    return None


def normalize_firms_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Convert different FIRMS/Kaggle column naming conventions into
    the standard SIH-26 schema.
    """

    dataframe = dataframe.copy()

    output = pd.DataFrame(index=dataframe.index)

    for standard_name, aliases in COLUMN_ALIASES.items():
        source_column = _find_column(dataframe, aliases)

        if source_column is not None:
            output[standard_name] = dataframe[source_column]
        else:
            output[standard_name] = pd.NA

    # ---------------------------------------------------------------
    # Numeric conversion
    # ---------------------------------------------------------------

    numeric_columns = [
        "latitude",
        "longitude",
        "frp",
        "brightness",
        "brightness_i5",
        "confidence",
    ]

    for column in numeric_columns:
        output[column] = pd.to_numeric(
            output[column],
            errors="coerce",
        )

    # ---------------------------------------------------------------
    # Date/time normalization
    # ---------------------------------------------------------------

    output["acquisition_date"] = pd.to_datetime(
        output["acquisition_date"],
        errors="coerce",
    )

    # FIRMS acquisition time is frequently HHMM.
    output["acquisition_time"] = (
        output["acquisition_time"]
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(4)
    )

    # ---------------------------------------------------------------
    # Basic geographic validation
    # ---------------------------------------------------------------

    output.loc[
        ~output["latitude"].between(-90, 90),
        "latitude",
    ] = pd.NA

    output.loc[
        ~output["longitude"].between(-180, 180),
        "longitude",
    ] = pd.NA

    # ---------------------------------------------------------------
    # Remove records without a valid location/date.
    # ---------------------------------------------------------------

    output = output.dropna(
        subset=[
            "latitude",
            "longitude",
            "acquisition_date",
        ]
    )

    # ---------------------------------------------------------------
    # Add source metadata.
    # ---------------------------------------------------------------

    output["source"] = "FIRMS"

    # Stable row identifier for later deduplication.
    output["detection_id"] = [
        f"firms_{index}"
        for index in output.index
    ]

    output = output.reset_index(drop=True)

    return output


def load_firms_csv(path: str | Path) -> pd.DataFrame:
    """
    Load a FIRMS CSV file and normalize it.
    """

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"FIRMS file not found: {path}"
        )

    dataframe = pd.read_csv(path)

    return normalize_firms_dataframe(dataframe)


def save_normalized_firms(
    dataframe: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Save normalized FIRMS data as Parquet.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        output_path,
        index=False,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Normalize a NASA FIRMS CSV for SIH-26."
    )

    parser.add_argument(
        "input",
        help="Path to FIRMS CSV",
    )

    parser.add_argument(
        "--output",
        default="data/intermediate/cleaned_firms/firms.parquet",
        help="Output Parquet path",
    )

    args = parser.parse_args()

    firms = load_firms_csv(args.input)

    save_normalized_firms(
        firms,
        args.output,
    )

    print(f"Loaded records: {len(firms)}")
    print(f"Saved to: {args.output}")
    print("\nColumns:")
    print(list(firms.columns))