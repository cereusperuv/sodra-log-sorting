# -*- coding: utf-8 -*-

"""Utils for database manipulation."""

from pathlib import Path

import pandas as pd
import pymssql
from box import Box

from log_sorting.constants import SQL_EXTENSION


def create_azure_sql_connection(
    db_config: Box,
) -> pymssql.Connection:
    """Create a connection to Azure SQL server DB.
    
    :param db_config: Database connection configuration.
    :type db_config: Box
    :return: Database connection.
    :type return: pymssql.Connection
    """
    return pymssql.connect(
        server=db_config.server,
        user=f"sodra.com\\{db_config.user}",
        password=db_config.password,
        database=db_config.database,
    )


def create_sql_query(*query_lines: str) -> str:
    """Create SQL query from lines.
    
    :param query_lines: Individual lines in query.
    :type query_lines: str
    :return: SQL query.
    :type return: str
    """
    return "\n".join(query_lines)


def load_sql_query(
    query_name: str,
    sql_dir: Path,
) -> str:
    """Load a SQL query from SQL directory.

    :param query_name: Name of SQL query file.
    :type query_name: str
    :param sql_dir: SQL query directory path.
    :type sql_dir: pathlib.Path
    :return: SQL query.
    :type return: str
    """
    file_path = sql_dir / f"{query_name}.{SQL_EXTENSION}"
    with open(file_path, 'r') as f:
        query = f.read()
    
    return query


def read_to_pandas(
    connection_config: Box,
    sql_query: str,
) -> pd.DataFrame:
    """Read data to pandas dataframe via SQL query.

    :param connection_config: Connection configuration.
    :type connection_config: Box
    :param sql_query: SQL query.
    :type sql_query: str
    :return: Result from SQL query.
    :rtype: pd.DataFrame
    """
    with create_azure_sql_connection(connection_config) as conn:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        cursor.close()
    
    return df
