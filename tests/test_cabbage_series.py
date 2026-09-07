import sys
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Add project root
# --------------------------------------------------

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


# --------------------------------------------------
# Load series summary
# --------------------------------------------------

file_path = (
    project_root
    / "data"
    / "processed"
    / "series_summary.csv"
)


print("\nLoading series summary...")
print("-" * 60)

series_summary = pd.read_csv(file_path)

print(
    f"Loaded {len(series_summary):,} series."
)


# --------------------------------------------------
# Filter Cabbage
# --------------------------------------------------

cabbage = series_summary[
    series_summary["Commodity"]
    .str.strip()
    .str.lower()
    == "cabbage"
].copy()


print("\nCabbage series")
print("-" * 60)

print(
    f"Total Cabbage series: "
    f"{len(cabbage):,}"
)


# --------------------------------------------------
# Filter for sufficiently long series
# --------------------------------------------------

usable = cabbage[
    cabbage["observations"] >= 180
].copy()


print(
    f"Cabbage series with >= 180 observations: "
    f"{len(usable):,}"
)


# --------------------------------------------------
# Rank strong series
# --------------------------------------------------

usable = usable.sort_values(
    [
        "continuity_pct",
        "observations"
    ],
    ascending=False
)


# --------------------------------------------------
# Display best candidates
# --------------------------------------------------

print("\nTop 30 Cabbage Series")
print("-" * 60)

columns = [
    "State",
    "District",
    "Market",
    "Commodity",
    "Variety",
    "Grade",
    "observations",
    "start_date",
    "end_date",
    "median_gap_days",
    "max_gap_days",
    "continuity_pct"
]

print(
    usable[
        columns
    ]
    .head(30)
    .to_string(index=False)
)


# --------------------------------------------------
# Save candidates
# --------------------------------------------------

output_path = (
    project_root
    / "data"
    / "processed"
    / "cabbage_series_candidates.csv"
)

usable.to_csv(
    output_path,
    index=False
)


print("\n")
print("-" * 60)

print(
    f"Cabbage candidates saved to:\n"
    f"{output_path}"
)

print("\nAnalysis completed successfully.")