# -*- coding: utf-8 -*-

"""Log sorting package entry point."""

from box import Box
from jinja2 import Template

from log_sorting.config import load_config
from log_sorting.constants import (
    CONFIG_DIR,
    CSV_EXTENSION,
    DATA_DIR,
    CONFIG_FILES,
    SQL_DIR,
)
from log_sorting.db_utils import load_sql_query, read_to_pandas
from log_sorting.functions import (
    load_and_preprocess_red_sheet,
    postprocess_log_sorting_data,
)


def pipeline(config: Box):
    """Log sorting pipeline.
    
    :param config: Run configuration.
    :type config: Box
    :return: None
    """
    # Load red sheet & parse query config
    red_sheet, query_config = load_and_preprocess_red_sheet(
        file_name=config.file_names.red_sheet,
        file_dir=DATA_DIR,
    )
    # Make sql query
    q = load_sql_query(config.sql.base_query, SQL_DIR)
    prepped_query = Template(q).render(
        species=config.sql.species,
        start_date=config.sql.start_date,
        end_date=config.sql.end_date,
        diameter_groups=query_config,
    )
    # Read from database
    df = read_to_pandas(config.database.mapptvr, prepped_query)
    # Merge result with red sheet & sort
    df = postprocess_log_sorting_data(df, red_sheet)
    # Write results
    file_path = DATA_DIR / f"{config.file_names.output}.{CSV_EXTENSION}"
    df.to_csv(file_path, sep=";", index=False)


if __name__ == "__main__":
    # Load run configuration
    config = load_config(CONFIG_FILES, CONFIG_DIR)
    # Run pipeline
    pipeline(config)
