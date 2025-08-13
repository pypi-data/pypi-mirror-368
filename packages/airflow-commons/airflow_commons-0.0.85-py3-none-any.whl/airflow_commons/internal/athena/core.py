from airflow_commons.internal.athena.constants import EMPTY_STRING
from airflow_commons.internal.athena.query import get_add_partition_sql
from airflow_commons.internal.util.log_utils import get_logger

logger = get_logger("AthenaCore")


def add_partitions(
    client,
    result_bucket: str,
    result_folder: str,
    database: str,
    table: str,
    partitions: list,
):
    """
    Adds requested hive-like partitions to given Athena table
    :param client: Athena service
    :param result_bucket: Result bucket name
    :param result_folder: Result folder name
    :param database: Database name
    :param table: Table name
    :param partitions: Partitions dictionaries as key value pairs
    """
    sql = get_add_partition_sql(table=table, partitions=partitions)
    if sql == EMPTY_STRING:
        return
    return query(client, sql, result_bucket, result_folder, database)


def query(
    client,
    sql: str,
    result_bucket: str,
    result_folder: str,
    database: str,
):
    """
    Runs given query on Athena using AthenaClient
    :param client: Athena service
    :param sql: Query to run
    :param result_bucket: Result bucket name
    :param result_folder: Result folder name
    :param database: Database name
    """
    try:
        response = client.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={"Database": database},
            ResultConfiguration={
                "OutputLocation": "s3://" + result_bucket + "/" + result_folder + "/"
            },
        )
    except Exception as e:
        logger.warn("An error occurred while running query")
        raise Exception(str(e)) from e
    return response


def get_query_execution(client, query_execution_id: str):
    """
    Returns current state of an athena query
    :param client: Athena service
    :param query_execution_id: Unique execution id of the query
    """
    return client.get_query_execution(QueryExecutionId=query_execution_id)
