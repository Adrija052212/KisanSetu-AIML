from pathlib import Path
import pandas as pd


def load_market_data(file_path):
    """
    Load agricultural market-price data from a CSV or Excel file.

    Parameters:
        file_path (str or Path): Path to the dataset.

    Returns:
        pandas.DataFrame: Loaded market-price data.
    """

    # Convert the given path into a Path object
    file_path = Path(file_path)

    # Check whether the file exists
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    # Get the file extension
    extension = file_path.suffix.lower()

    # Load CSV files
    if extension == ".csv":
        df = pd.read_csv(file_path)

    # Load Excel files
    elif extension in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)

    # Reject unsupported file formats
    else:
        raise ValueError(
            "Unsupported file format. "
            "Please use a CSV or Excel file."
        )

    # Check whether the dataset is empty
    if df.empty:
        raise ValueError("The dataset is empty.")

    # Return the loaded DataFrame
    return df


if __name__ == "__main__":
    print("Market data loader is ready.")