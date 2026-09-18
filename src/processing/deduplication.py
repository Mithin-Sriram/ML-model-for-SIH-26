from __future__ import annotations

import pandas as pd


def deduplicate_detections(
    dataframe: pd.DataFrame,
    coordinate_precision: int = 4,
) -> pd.DataFrame:
    """
    Remove likely duplicate thermal detections.

    Coordinates are rounded before duplicate comparison because
    different source files may represent the same detection with
    tiny floating-point differences.
    """

    df = dataframe.copy()

    required = [
        "latitude",
        "longitude",
        "acquisition_date",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df["_lat_key"] = df["latitude"].round(
        coordinate_precision
    )

    df["_lon_key"] = df["longitude"].round(
        coordinate_precision
    )

    dedup_columns = [
        "_lat_key",
        "_lon_key",
        "acquisition_date",
    ]

    for column in [
        "acquisition_time",
        "satellite",
        "instrument",
    ]:
        if column in df.columns:
            dedup_columns.append(column)

    before = len(df)

    df = df.drop_duplicates(
        subset=dedup_columns,
        keep="first",
    )

    removed = before - len(df)

    df = df.drop(
        columns=[
            "_lat_key",
            "_lon_key",
        ]
    )

    df = df.reset_index(drop=True)

    print(f"Records before deduplication: {before}")
    print(f"Duplicates removed: {removed}")
    print(f"Records after deduplication: {len(df)}")

    return df