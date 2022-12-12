# -*- coding: utf-8 -*-

"""Util functions."""

from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd


def create_monotonic_key_from_columns(
    data: pd.DataFrame,
    columns: List[str],
    key_column: str,
) -> Tuple[pd.DataFrame]:
    """Create monotonic key based on column values.
    
    Note: Input data assumed sorted.
    
    :param data: Data.
    :param columns: Names of columns to base key on.
    :param key_column: Name of key column.
    :return: Data with key column, ranging from 0 to total number of
    groups - 1, and a mapping from key values to original column values.
    """
    # Create key column
    keys = (
        data
        .groupby(by=columns, as_index=False)
        .ngroup()
    )
    data.insert(
        loc=0,
        column=key_column,
        value=keys,
    )
    # Create key -> columns mapping
    mapping = data[[key_column]+columns].drop_duplicates()
    # Select columns
    data = data.drop(columns=columns)
    
    return data, mapping


def get_from_mapping(
    mapping: Dict[Union[int, str], Any],
    key: Union[int, str],
    key_desc: Optional[str] = None,
) -> Any:
    """Get a value from a mapping in a safe manner.
    
    :param mapping: Dict with mapping to get value from.
    :param key: Key for value to fetch.
    :param key_desc: Key description for error message.
    :return: Value from mapping.
    """
    value = mapping.get(key, None)
    if value is None:
        key_desc = "Key value" if key_desc is None else key_desc
        raise ValueError(
            f"{key_desc} '{key}' not supported. "
            f"Available options: {list(mapping.keys())}"
        )
        
    return value


def strings_to_lowercase(
    df: pd.DataFrame,
    exclude_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Convert all string columns in a DataFrame to lower case.

    :param df: DataFrame to convert.
    :return: DataFrame with all string columns converted to lower case.
    """
    # Catch case where dataframe has been squeezed to series.
    if isinstance(df, pd.Series):
        return df.str.lower() if df.dtype == "object" else df

    for column_ in df.columns[df.dtypes == "object"]:
        if not exclude_columns or (exclude_columns and column_ not in exclude_columns):
            df[column_] = df[column_].str.lower()

    return df


def column_names_to_lowercase(
    data: Union[pd.DataFrame, pd.Series],
) -> Union[pd.DataFrame, pd.Series]:
    """Convert all column names to lower case.

    :param data: Pandas dataframe or series.
    :return: DataFrame with lower case column names.
    """
    # For series
    if isinstance(data, pd.Series):
        data.name = data.name.lower()
    elif isinstance(data, pd.DataFrame):
        data.columns = [c.lower() for c in data.columns]
    else:
        raise ValueError(
            "Only supports 'pd.Series' & 'pd.DataFrame'.",
        )

    return data


def replace_string(
    data: pd.DataFrame,
    column: str,
    contains: str,
    replacement: str,
) -> pd.DataFrame:
    """Replace string column value based on content.
    
    :param data: Data with string column.
    :param column: Name of string column.
    :param contains: String content to look for.
    :param replacement: Replacement for entire value.
    :return: Data with replaced values.
    """
    replacement_mask = (
        data[column]
        .fillna("")
        .str.contains(contains)
    )
    data.loc[replacement_mask, column] = replacement
    
    return data


def map_and_insert(
    data: pd.DataFrame,
    column: str,
    mapped_column: str,
    mapping: Dict[Any, Any],
    location: str,
    dropna: bool = False,
) -> pd.DataFrame:
    """Map a column and insert mapped value.
    
    :param data: Data with column to map.
    :param column: Name of column to map.
    :param mapped_column: Name of mapped column.
    :param mapping: Key-value dict with mapping.
    :param dropna: Drop mapping-NA:s or not.
    :return: Data with mapped column.
    """
    # Drop NA:s if asked for
    if dropna:
        mask = data[column].isin(list(mapping.keys()))
        data = data.loc[mask].reset_index(drop=True)
    # Insert data
    allowed_locations = ["left", "right", "end"]
    if location in allowed_locations:
        insertion_index = data.columns.get_loc(column)
        if location == "right":
            insertion_index += 1
        elif location == "end":
            insertion_index = data.shape[1]
    else:
        raise ValueError(
            f"Location '{location}' not supported, "
            f"valid choices are {allowed_locations}."
        )
    data.insert(
        loc=insertion_index,
        column=mapped_column,
        value=data[column].map(mapping),
    )

    return data
