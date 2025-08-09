"""
Add metadata back to the predicted DataFrame

Author: Shahin ABDOUL SOUKOUR - Inria
Maintainer: Shahin ABDOUL SOUKOUR - Inria
"""

import pandas as pd


def add_metadata_to_predictions_from_dataframe(predicted_df, column_names):
    """
    Add metadata (column names) back to the predicted DataFrame.

    Args:
        predicted_df: DataFrame containing the predictions without metadata.
        column_names: List of column names corresponding to the predictions.

    Returns:
        Pandas DataFrame with metadata (column names).
    """
    try:
        # Check if the number of columns matches the column names
        if predicted_df.shape[1] != len(column_names):
            raise ValueError(
                "Mismatch between the number of columns in the "
                "predicted DataFrame and column names."
            )

        # Assign column names
        predicted_df.columns = column_names

        return predicted_df
    except ValueError as e:
        print(e)
        return pd.DataFrame()
