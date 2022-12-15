# -*- coding: utf-8 -*-

"""Util functions."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from log_sorting.constants import (
    CROSS_JOIN_COL,
    CSV_EXTENSION,
    DATE_COL,
    DESIRED_COL,
    DIAMETER_COL,
    DIAMETER_FILLNA_COL,
    DIAMETER_GROUP_COL,
    DIAMETER_INTERVAL_COL,
    LENGTH_COL,
    LENGTH_INTERVAL_COL,
    LOT_ID_COL,
    QUERY_CONFIG_COLS,
    RED_SHEET_COLS,
    SPECIES_COL,
)


def create_interval_column(
    data: pd.DataFrame,
    col: str,
    interval_col: str,
    fillna_col: Optional[str] = None,
) -> pd.DataFrame:
    """Create column with intervals from single column with values.
    
    Intervals are returned as lists and interval values are created from column value
    and subsequent column value.

    :param data: Data with column with values to create intervals from.
    :type data: pd.DataFrame
    :param col: Column with values to create intervals from.
    :type col: str
    :param interval_col: Name of column with intervals.
    :type interval_col: str
    :param fillna_col: Column to fill NA:s from, defaults to -1.
    :type fillna_col: Optional[str], optional
    :return: Data with interval column.
    :rtype: pd.DataFrame
    """
    # Create column with upper interval limit
    values = list(data[col].sort_values().unique())
    to_col_map = {x: y for x, y in zip(values, values[1:]+[None])}
    to_col = col + "_to"
    data[to_col] = data[col].map(to_col_map)
    # Fill NaN:s at end
    if fillna_col:
        data[to_col] = data[to_col].fillna(data[fillna_col])
        data = data.drop(columns=[fillna_col])
    else:
        data[to_col] = data[to_col].fillna(-1)
    # Set data type
    data[to_col] = data[to_col].astype(data[col].dtype)
    # Create interval column
    data[interval_col] = data[[col, to_col]].values.tolist()
    # Drop unecessary columns
    data = data.drop(columns=[col, to_col])
    
    return data


def load_and_preprocess_red_sheet(
    file_name: str,
    file_dir: Path,
) -> Tuple[pd.DataFrame, List[Dict[str, Union[List[int], List[List[int]]]]]]:
    """Load and pre-process red sheet data.

    :param species: Species in red sheet file.
    :type species: int
    :param file_name: Name of red sheet data file.
    :type file_name: str
    :param file_dir: Red sheet data file directory.
    :type file_dir: Path
    :return: _description_
    :rtype: pd.DataFrame
    """
    # Load data
    file_path = file_dir / f"{file_name}.{CSV_EXTENSION}"
    red_sheet = pd.read_csv(file_path)
    # Rename length column
    red_sheet = red_sheet.rename(
        columns={"Unnamed: 0": LENGTH_COL},
    )
    # Fill missing zeros
    red_sheet = red_sheet.fillna(0)
    # Add 0-length row at top
    zero_row = pd.DataFrame(
        data=np.array([[0]*red_sheet.shape[1]]),
        columns=red_sheet.columns,
    )
    red_sheet = pd.concat(
        objs=[zero_row, red_sheet],
        ignore_index=True,
    )
    # Unpivot
    red_sheet = pd.melt(
        frame=red_sheet,
        id_vars=[LENGTH_COL],
        var_name=DIAMETER_GROUP_COL,
        value_name=DESIRED_COL,
    )
    # Create SQL query config
    query_config = red_sheet.copy()
    # Prep diameter intervals
    query_config[[DIAMETER_COL, DIAMETER_FILLNA_COL]] = (
        query_config[DIAMETER_GROUP_COL]
        .str.split("-", expand=True)
    )
    query_config[DIAMETER_COL] = 10 * (
        query_config[DIAMETER_COL]
        .astype(int)
    )
    query_config = create_interval_column(
        data=query_config,
        col=DIAMETER_COL,
        interval_col=DIAMETER_INTERVAL_COL,
        fillna_col=DIAMETER_FILLNA_COL,
    )
    # Prep length intervals
    query_config[LENGTH_COL] = (10 * query_config[LENGTH_COL]).astype(int)
    query_config = create_interval_column(
        data=query_config,
        col=LENGTH_COL,
        interval_col=LENGTH_INTERVAL_COL,
    )
    # Make dict
    query_config[DIAMETER_INTERVAL_COL] = query_config[DIAMETER_INTERVAL_COL].map(tuple)
    query_config = (
        query_config[QUERY_CONFIG_COLS]
        .groupby([DIAMETER_GROUP_COL, DIAMETER_INTERVAL_COL], as_index=False)
        .agg(lambda x: x.to_list())
    )
    query_config[DIAMETER_INTERVAL_COL] = query_config[DIAMETER_INTERVAL_COL].map(list)
    query_config = query_config.to_dict(orient="records")
    
    return red_sheet[RED_SHEET_COLS], query_config


def postprocess_log_sorting_data(
    log_sorting_data: pd.DataFrame,
    red_sheet_data: pd.DataFrame,
) -> pd.DataFrame:
    """Post-process log sorting data.

    :param log_sorting_data: Log sorting data.
    :type log_sorting_data: pd.DataFrame
    :param red_sheet_data: Red sheet data.
    :type red_sheet_data: pd.DataFrame
    :return: Post-processed data.
    :rtype: pd.DataFrame
    """
    # Create base data as Cartesian product
    species_dates_lot_ids = (
        log_sorting_data[[SPECIES_COL, DATE_COL, LOT_ID_COL]]
        .drop_duplicates()
    )
    species_dates_lot_ids[CROSS_JOIN_COL] = 0
    diameter_groups_lengths = (
        log_sorting_data[[DIAMETER_GROUP_COL, LENGTH_COL]]
        .drop_duplicates()
    )
    diameter_groups_lengths[CROSS_JOIN_COL] = 0
    base_df = (
        species_dates_lot_ids
        .merge(
            right=diameter_groups_lengths,
            on=CROSS_JOIN_COL,
            how="outer",
            validate="m:m",
        )
        .drop(columns=[CROSS_JOIN_COL])
    )
    # Merge base date with sorting & red sheet data
    sort_cols = [
        SPECIES_COL,
        DATE_COL,
        LOT_ID_COL,
        DIAMETER_GROUP_COL,
        LENGTH_COL,
    ]
    df = (
        base_df
        .merge(
            right=log_sorting_data,
            on=[
                SPECIES_COL,
                DATE_COL,
                LOT_ID_COL,
                DIAMETER_GROUP_COL,
                LENGTH_COL,
            ],
            how="left",
            validate="1:1",
        )
        .astype({LENGTH_COL: float})
        .merge(
            right=red_sheet_data,
            on=[
                DIAMETER_GROUP_COL,
                LENGTH_COL,
            ],
            how="inner",
            validate="m:1",
        )
        .fillna(0)
        .sort_values(sort_cols)
    )
    
    return df
