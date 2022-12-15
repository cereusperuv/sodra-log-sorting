# -*- coding: utf-8 -*-

"""Constants for all notebooks in <project name>."""

from configs import CONFIG_DIR
from data import DATA_DIR
from sql import SQL_DIR


# Directories
CONFIG_DIR = CONFIG_DIR
DATA_DIR = DATA_DIR
SQL_DIR = SQL_DIR

# Config files (in order)
CONFIG = "config"
CONFIG_FILES = [
    CONFIG,
]

# File extensions
CSV_EXTENSION = "csv"
PARQUET_EXTENSION = "parquet"
SQL_EXTENSION = "sql"
TXT_EXTENSION = "txt"
XLS_EXTENSION = "xls"
XLSX_EXTENSION = "xlsx"
YAML_EXTENSION = "yaml"

# Column names
CROSS_JOIN_COL = "cross_join"
DATE_COL = "date"
DESIRED_COL = "desired"
DIAMETER_COL = "diameter"
DIAMETER_FILLNA_COL = "diameter_fillna"
DIAMETER_GROUP_COL = "diameter_group"
DIAMETER_INTERVAL_COL = "diameter_interval"
LENGTH_COL = "length"
LENGTH_INTERVAL_COL = "length_interval"
LOT_ID_COL = "lot_id"
SPECIES_COL = "species"

# Column sets
QUERY_CONFIG_COLS = [
    DIAMETER_GROUP_COL,
    DIAMETER_INTERVAL_COL,
    LENGTH_INTERVAL_COL
]
RED_SHEET_COLS = [
    DIAMETER_GROUP_COL,
    LENGTH_COL,
    DESIRED_COL,
]
