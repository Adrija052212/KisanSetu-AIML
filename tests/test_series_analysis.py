import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.data.loader import load_market_data
from src.data.standardizer import standardize_market_data
from src.data.preparation import prepare_market_data
from src.data.series_analyzer import analyze_time_series


# --------------------------------------------------
# Dataset path
# --------------------------------------------------

file_path = (
    project_root
    / "data"
    / "raw"
    / "SIH_Cleaned_Dataset.xlsx"
)


# --------------------------------------------------
# Load
# --------------------------------------------------

print("Loading dataset...")
df = load_market_data(file_path)

print(f"Loaded rows: {len(df):,}")


# --------------------------------------------------
# Standardize
# --------------------------------------------------

print("\nStandardizing dataset...")

df = standardize_market_data(df)


# --------------------------------------------------
# Prepare
# --------------------------------------------------

print("\nPreparing dataset...")

df = prepare_market_data(df)


# --------------------------------------------------
# Analyze time series
# --------------------------------------------------

print("\nAnalyzing time series...")

series_summary = analyze_time_series(
    df,
    group_columns=[
        "State",
        "District",
        "Market",
        "Commodity",
        "Variety",
        "Grade"
    ]
)


# --------------------------------------------------
# Basic summary
# --------------------------------------------------

print("\n")
print("=" * 60)
print("TIME SERIES SUMMARY")
print("=" * 60)

print(
    f"Total observations: {len(df):,}"
)

print(
    f"Unique time series: "
    f"{len(series_summary):,}"
)

print(
    f"Average observations per series: "
    f"{series_summary['observations'].mean():.2f}"
)

print(
    f"Median observations per series: "
    f"{series_summary['observations'].median():.0f}"
)

print(
    f"Maximum observations in a series: "
    f"{series_summary['observations'].max():,}"
)


# --------------------------------------------------
# Series length distribution
# --------------------------------------------------

print("\n")
print("=" * 60)
print("SERIES LENGTH DISTRIBUTION")
print("=" * 60)

for threshold in [30, 60, 90, 180, 270]:

    count = (
        series_summary["observations"] >= threshold
    ).sum()

    print(
        f"Series with >= {threshold:3} observations: "
        f"{count:,}"
    )


# --------------------------------------------------
# Continuity
# --------------------------------------------------

print("\n")
print("=" * 60)
print("CONTINUITY")
print("=" * 60)

print(
    f"Mean continuity: "
    f"{series_summary['continuity_pct'].mean():.2f}%"
)

print(
    f"Median continuity: "
    f"{series_summary['continuity_pct'].median():.2f}%"
)

print(
    f"Maximum continuity: "
    f"{series_summary['continuity_pct'].max():.2f}%"
)


# --------------------------------------------------
# Top longest series
# --------------------------------------------------

print("\n")
print("=" * 60)
print("TOP 20 LONGEST SERIES")
print("=" * 60)

top_series = (
    series_summary
    .sort_values(
        "observations",
        ascending=False
    )
    .head(20)
)

print(
    top_series[
        [
            "State",
            "District",
            "Market",
            "Commodity",
            "Variety",
            "Grade",
            "observations",
            "start_date",
            "end_date",
            "continuity_pct"
        ]
    ].to_string(index=False)
)


# --------------------------------------------------
# Save summary
# --------------------------------------------------

output_path = (
    project_root
    / "data"
    / "processed"
    / "series_summary.csv"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

series_summary.to_csv(
    output_path,
    index=False
)

print("\n")
print(
    f"Series summary saved to:\n{output_path}"
)