from airflow_commons.internal.athena.constants import EMPTY_STRING
from airflow_commons.internal.util.file_utils import read_sql
from airflow_commons.internal.util.log_utils import get_logger
from airflow_commons.resources.athena import ADD_PARTITION_STATEMENT_FILE
from airflow_commons.resources.glossary import (
    OPEN_PARENTHESIS,
    EQUALS_SIGN,
    CLOSE_PARENTHESIS,
    WHITE_SPACE,
    DOUBLE_QUOTE,
    DOT,
    COMMA,
)

PARTITION = "PARTITION"

logger = get_logger("AthenaQuery")


def get_add_partition_sql(table: str, partitions: list):
    partition_statements = []
    for partition_dict in partitions:
        partition_definition = (
            PARTITION
            + OPEN_PARENTHESIS
            + COMMA.join(
                str(key) + EQUALS_SIGN + str(value)
                for key, value in partition_dict.items()
            )
            + CLOSE_PARENTHESIS
        )
        partition_statements.append(partition_definition)
    if not partition_statements:
        logger.info(
            "There are no partition statements to proceed, please check the partitions argument."
        )
        return EMPTY_STRING
    return read_sql(
        ADD_PARTITION_STATEMENT_FILE,
        table_name=table,
        all_partitions=WHITE_SPACE.join(partition_statements),
    )
