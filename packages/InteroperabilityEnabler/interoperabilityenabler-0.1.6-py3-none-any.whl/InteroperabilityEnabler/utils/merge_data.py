"""
Merge data

Author: Shahin ABDOUL SOUKOUR - Inria
Maintainer: Shahin ABDOUL SOUKOUR - Inria
"""

import numpy as np
import pandas as pd

def merge_predicted_data(df_initial, predicted_df_with_metadata):
    """
    Merge predicted data into the initial DataFrame by matching column names.
    Add `np.nan` (proper null) for missing columns in the predicted data.

    Args:
        df_initial: DataFrame containing the original selected columns.
        predicted_df_with_metadata: DataFrame containing the predicted data with metadata.

    Returns:
        A merged Pandas DataFrame with `np.nan` for missing columns.
    """
    try:
        # Get all unique columns from both DataFrames
        all_columns = set(df_initial.columns).union(
            set(predicted_df_with_metadata.columns)
        )

        # Ensure all columns are present in both DataFrames
        for col in all_columns:
            if col not in df_initial.columns:
                df_initial[col] = np.nan  # Use np.nan instead of "null"
            if col not in predicted_df_with_metadata.columns:
                predicted_df_with_metadata[col] = np.nan  # Use np.nan instead of "null"

        # Reorder columns to match the initial DataFrame's order
        df = df_initial[sorted(all_columns)]
        predicted_df_with_metadata = predicted_df_with_metadata[sorted(all_columns)]

        # Merge the DataFrames
        merged_df = pd.concat([df, predicted_df_with_metadata], ignore_index=True)

        return merged_df
    except Exception as e:
        print(f"Error during merging: {e}")
        return pd.DataFrame()
