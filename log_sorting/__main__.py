# -*- coding: utf-8 -*-

"""Log sorting package entry point."""

import pandas as pd

from configs import CONFIG_DIR
from log_sorting.constants import CONFIG_FILES
from log_sorting.config import load_config
from log_sorting.db_utils import create_azure_sql_connection, load_sql_query
from sql import SQL_DIR

def main():
    """Run the main logic of the script."""
    config = load_config(CONFIG_FILES, CONFIG_DIR)
    
    q = load_sql_query("get-log-sorting-data", SQL_DIR)
    print(q)
    
    with create_azure_sql_connection(config.mapptvr) as conn:
        cursor = conn.cursor()
        cursor.execute(q)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        cursor.close()
    
    print(df.head())

if __name__ == "__main__":
    main()
