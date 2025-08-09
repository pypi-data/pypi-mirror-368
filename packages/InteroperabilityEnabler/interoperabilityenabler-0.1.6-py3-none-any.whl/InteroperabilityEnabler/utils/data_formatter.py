"""
Data Formatter:
To convert the data expressed in various format (CSV, XLS, XLSX and NGSI-LD)
into the SEDIMARK internal format, i.e., pandas DataFrame.
NGSI-LD was selected as the primary format.

Author: Shahin ABDOUL SOUKOUR - Inria
Maintainer: Shahin ABDOUL SOUKOUR - Inria
"""

import json
import pandas as pd


def data_formatter(data, sep="__"):
    """
    Formats input data (in JSON) into a structured DataFrame via the data_to_dataframe function.
    The function accepts either a file path to a JSON file, a raw JSON-like string,
    or a Python object (dictionary or list). It processes the input and leverages the provided separator
    to convert the data into a DataFrame format.

    If the input is not in a supported format or type, an error is raised or caught.

    Args:
        data: The input data to be formatted. Can be a file path (ending in .json), a
            JSON-like string, or a Python object like a dictionary or list.
        sep: The separator string used in formatting. Defaults to "__".

    Returns:
        A DataFrame-like object containing the structured representation of the input data,
        or a tuple of `None, None` if processing fails.
    """
    try:
        if isinstance(data, str):
            if data.endswith(".json"):
                with open(data, "r", encoding="utf-8") as file:
                    raw_data = json.load(file)
                    return data_to_dataframe(raw_data, sep=sep)
            else:
                raise ValueError(
                    "Unsupported file format or content. Must be .json or raw JSON-like content"
                )
        elif isinstance(data, (dict, list)):
            return data_to_dataframe(data, sep=sep)
        else:
            raise ValueError(
                "Unsupported input type. Must be a file path or JSON object."
            )
    except Exception as e:
        print(f"Error processing data: {e}")
        return None, None


def data_to_dataframe(raw_data, sep):
    """
    Converts time-series data (in JSON) into two structured DataFrames: a context DataFrame
    and a time series DataFrame.
    The context DataFrame contains the id and type of the entity. It is a single-row DataFrame.
    The time series DataFrame contains flattened and chronologically sorted time-based data (data points).

    Args:
        raw_data: Dict containing time-series data.
        sep: String separator used to create flat column names by combining keys
            and attributes from the hierarchical structure.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two pandas DataFrames:
            - A context DataFrame.
            - A time series DataFrame where each row corresponds to a single observed
              timestamp, flattened with attributes prefixed with their associated key.
    """
    # Build context DataFrame
    context_keys = ["id", "type"]
    context = {k: raw_data[k] for k in context_keys}
    context_df = pd.DataFrame([context])

    # Build dynamic flat rows
    rows = []

    for key, val_list in raw_data.items():
        if (
            isinstance(val_list, list)
            and val_list
            and isinstance(val_list[0], dict)
            and "observedAt" in val_list[0]
        ):
            for entry in val_list:
                timestamp = entry["observedAt"]
                row = {"observedAt": timestamp}
                for attr_key, attr_val in entry.items():
                    if attr_key == "observedAt":
                        continue
                    row[f"{key}{sep}{attr_key}"] = attr_val
                rows.append(row)

    # Combine and reshape
    time_series_df = pd.DataFrame(rows)

    # Handle potential duplicates by grouping
    time_series_df = time_series_df.groupby("observedAt").first().reset_index()

    # Sort chronologically
    time_series_df["observedAt"] = pd.to_datetime(time_series_df["observedAt"])
    time_series_df = time_series_df.sort_values("observedAt").reset_index(drop=True)

    # Convert to UNIX timestamp
    time_series_df["observedAt"] = time_series_df["observedAt"].astype(int) // 10**9

    return context_df, time_series_df