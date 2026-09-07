import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


# --------------------------------------------------
# File path
# --------------------------------------------------

file_path = (
    project_root
    / "data"
    / "processed"
    / "series_summary.csv"
)


# --------------------------------------------------
# Load series summary
# --------------------------------------------------

print("\nLoading series summary...")
print("-" * 60)

series_summary = pd.read_csv(file_path)

print(
    f"Loaded {len(series_summary):,} time series."
)


# --------------------------------------------------
# Columns used for analysis
# --------------------------------------------------

commodity_column = "Commodity"


# --------------------------------------------------
# Analyze commodities
# --------------------------------------------------

print("\nAnalyzing commodities...")
print("-" * 60)


commodity_analysis = (
    series_summary
    .groupby(commodity_column)
    .agg(
        total_series=("observations", "count"),

        average_observations=(
            "observations",
            "mean"
        ),

        median_observations=(
            "observations",
            "median"
        ),

        max_observations=(
            "observations",
            "max"
        ),

        average_continuity=(
            "continuity_pct",
            "mean"
        ),

        median_continuity=(
            "continuity_pct",
            "median"
        )
    )
    .reset_index()
)


# --------------------------------------------------
# Count usable series
# --------------------------------------------------

for minimum in [30, 60, 90, 180, 270]:

    counts = (
        series_summary
        .assign(
            usable=(
                series_summary["observations"]
                >= minimum
            )
        )
        .groupby(commodity_column)["usable"]
        .sum()
        .rename(
            f"series_ge_{minimum}"
        )
    )

    commodity_analysis = commodity_analysis.merge(
        counts,
        on=commodity_column,
        how="left"
    )


# --------------------------------------------------
# Sort by strong series
# --------------------------------------------------

commodity_analysis = (
    commodity_analysis
    .sort_values(
        [
            "series_ge_180",
            "series_ge_90",
            "average_continuity"
        ],
        ascending=False
    )
)


# --------------------------------------------------
# Display top commodities
# --------------------------------------------------

print("\nTop 30 Commodities")
print("-" * 60)

display_columns = [
    "Commodity",
    "total_series",
    "series_ge_30",
    "series_ge_60",
    "series_ge_90",
    "series_ge_180",
    "series_ge_270",
    "average_observations",
    "median_observations",
    "max_observations",
    "average_continuity",
    "median_continuity"
]

print(
    commodity_analysis[
        display_columns
    ]
    .head(30)
    .to_string(index=False)
)


# --------------------------------------------------
# Save analysis
# --------------------------------------------------

output_path = (
    project_root
    / "data"
    / "processed"
    / "commodity_analysis.csv"
)

commodity_analysis.to_csv(
    output_path,
    index=False
)


print("\n")
print("-" * 60)
print(
    f"Commodity analysis saved to:\n"
    f"{output_path}"
)

print("\nAnalysis completed successfully.")