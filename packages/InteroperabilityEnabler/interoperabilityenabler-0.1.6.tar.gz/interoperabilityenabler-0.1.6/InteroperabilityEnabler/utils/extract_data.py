"""
Data extraction

Author: Shahin ABDOUL SOUKOUR - Inria
Maintainer: Shahin ABDOUL SOUKOUR - Inria
"""

import pandas as pd


def extract_columns(df, column_indices):
    """
    Process specific columns in a CSV file (selected by index)
    and return them as a pandas DataFrame.

    Args:
        df: pandas DataFrame.
        column_indices: List of column indices to be selected (0-based index).

    Returns:
        The column names corresponding to the indices as a separate output
        with the DataFrame (with the selected columns).
    """
    try:
        # Check if the indices are valid
        if any(idx >= len(df.columns) or idx < 0 for idx in column_indices):
            raise ValueError(f"Invalid column indices: {column_indices}")

        # Map indices to column names
        # Retrieve the column names corresponding to the indices
        column_names = [df.columns[idx] for idx in column_indices]

        # Select only the desired columns by name
        selected_df = df[column_names]

        # Return the resulting DataFrame and metadata
        return selected_df, column_names

    except FileNotFoundError:
        print("Error: File not found.")
        return pd.DataFrame(), []
    except ValueError as e:
        print(e)
        return pd.DataFrame(), []
