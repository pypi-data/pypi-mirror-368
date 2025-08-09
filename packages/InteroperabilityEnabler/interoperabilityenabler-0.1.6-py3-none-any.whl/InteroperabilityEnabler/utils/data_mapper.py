"""
Data Mapper:
To convert the data from the internal formatting (pandas DataFrame) to the NGSI-LD format,
which is the standard adopted within SEDIMARK.

Author: Shahin ABDOUL SOUKOUR - Inria
Maintainer: Shahin ABDOUL SOUKOUR - Inria
"""
from datetime import datetime
import pandas as pd


def data_mapper(
    context_df: pd.DataFrame, time_series_df: pd.DataFrame, sep="__") -> dict:
    """
    Maps data from context and time series DataFrames into a structured dictionary format,
    while grouping attributes from time series data.

    Args:
        context_df (pd.DataFrame): The context DataFrame, expected to contain a single row
            representing context-level metadata.
        time_series_df (pd.DataFrame): The time series DataFrame containing multiple rows,
            with each row representing attribute values observed over time along with
            a timestamp field named "observedAt".
        sep (str): Separator string used to delineate composite field names in the time
            series DataFrame. Default is "__".

    Returns:
        dict: A dictionary containing context-level attributes along with grouped and
        timestamped attribute data from the time series DataFrame.
    """
    # Extract context as dictionary (single row)
    context = context_df.iloc[0].to_dict()

    # Initialize attribute grouping: attr -> list of observation dicts
    attribute_groups = {}

    for _, row in time_series_df.iterrows():
        ts = row["observedAt"]
        ts_iso = datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Temporarily collect fields for each attribute
        attr_temp = {}

        for col, val in row.items():
            if col == "observedAt":  # or pd.isna(val):
                continue

            if sep in col:
                attr, field = col.split(sep, 1)
                if attr not in attr_temp:
                    attr_temp[attr] = {}
                attr_temp[attr][field] = val

        # Add observedAt to each attribute's dict
        for attr, data in attr_temp.items():
            data["observedAt"] = ts_iso
            if attr not in attribute_groups:
                attribute_groups[attr] = []
            attribute_groups[attr].append(data)

    # Merge context and time-series attributes
    final_json = {**context, **attribute_groups}
    return final_json