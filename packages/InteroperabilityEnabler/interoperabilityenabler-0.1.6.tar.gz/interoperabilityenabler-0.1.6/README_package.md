## What is it?

Interoperability Enabler (IE) component is designed to facilitate seamless integration and interaction among various artefacts within the SEDIMARK ecosystem, including data, AI models, and service offerings.


## Key Feature

- Data Formatter - Convert JSON data (time-series data) into the SEDIMARK internal processing format (pandas DataFrames)
- Data Mapper – Convert data from pandas DataFrames into JSON
- Data Extractor – Extract relevant data from a pandas DataFrame
- Metadata Restorer – Restore metadata to a pandas DataFrame
- Data Merger – Merge two DataFrames by matching column names

## Installation

The source code can be found on GitHub at https://github.com/Sedimark/InteroperabilityEnabler.

To install the package, you can use pip:

```bash
pip install InteroperabilityEnabler
```

## Quick Start Examples

#### Data Formatter (to convert the input data into a pandas DataFrame)

```python
from InteroperabilityEnabler.utils.data_formatter import data_formatter

FILE_PATH="sample.json"
context_df, time_series_df = data_formatter(FILE_PATH)
```

#### Data Mapper (to convert the DataFrame into JSON format)

```python
from InteroperabilityEnabler.utils.data_mapper import data_mapper

data_json = data_mapper(context_df, time_series_df)
```

#### Data Extractor (to extract and return specific columns from a pandas DataFrame)

```python
from InteroperabilityEnabler.utils.extract_data import extract_columns

# Select columns by index
column_indices = [2, 5]

selected_df, selected_column_names = extract_columns(time_series_df, column_indices)

print("\nSelected DataFrame:")
print(selected_df)

print("\nSelected Column Names:")
print(selected_column_names)

```

#### Metadata Restorer (to restore column names into a pandas DataFrame)

```python
import pandas as pd
from InteroperabilityEnabler.utils.add_metadata import add_metadata_to_predictions_from_dataframe

PREDICTED_DATA = "predicted_data.csv" # example - prediction results from an AI model
predicted_df = pd.read_csv(PREDICTED_DATA, header=None)
predicted_df = add_metadata_to_predictions_from_dataframe(
    predicted_df, selected_column_names
)
```

#### Data Merger (merge two DataFrames)

```python
from InteroperabilityEnabler.utils.merge_data import merge_predicted_data

# To combine the original input data with the corresponding prediction results from an AI model
merged_df = merge_predicted_data(time_series_df, predicted_df)
```

## Acknowledgement

This software has been developed by [Inria](https://www.inria.fr/fr) under the [SEDIMARK(SEcure Decentralised Intelligent Data MARKetplace)](https://sedimark.eu/) project. 
SEDIMARK is funded by the European Union under the Horizon Europe framework programme [grant no. 101070074]. 
