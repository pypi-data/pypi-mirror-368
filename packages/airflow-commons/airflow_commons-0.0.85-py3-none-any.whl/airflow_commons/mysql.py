from airflow_commons.logger import get_logger

from airflow_commons.internal.util.file_utils import read_sql

from airflow_commons.internal.mysql.auth import get_session
from airflow_commons.internal.mysql.core import upsert
from airflow_commons.internal.mysql.core import update as update_util
from airflow_commons.internal.mysql.query_utils import get_delete_sql
from airflow_commons.internal.mysql.query_utils import get_select_all_sql
from airflow_commons.internal.mysql.query_utils import get_select_sql
from airflow_commons.internal.mysql.query_utils import get_row_count_sql
import pandas as pd


class MysqlOperator(object):
    def __init__(self, username, password, host, db_name):
        """
        Initializes a MysqlOperator instance

        :param username: database username
        :param password: database password
        :param host: database host
        :param db_name: database name
        :return:
        """
        self.Session = get_session(username, password, host, db_name)
        self.logger = get_logger("MysqlOperator")

    def write_to_mysql(
        self,
        values: dict,
        chunk_size: int,
        table_name: str,
        update_column_names: list = None,
    ):
        """
        :param values: values to write into database
        :param chunk_size: data size to upload at a time
        :param table_name: database table name to write
        :param update_column_names: columns to be updated, default is all columns except the primary key
        :return:
        """

        chunks = [values[i : i + chunk_size] for i in range(0, len(values), chunk_size)]
        with self.Session.begin() as session:
            i = 0
            for chunk in chunks:
                i += 1
                upsert(
                    values=chunk,
                    session=session,
                    table_name=table_name,
                    update_column_names=update_column_names,
                )

    def delete(
        self,
        table_name: str,
        where_statement_file: str,
        where_statement_params: dict = None,
    ):
        """
        Runs a delete query on given table, and removes rows that conform where condition

        :param table_name: table name
        :param where_statement_file: relative location of where statement sql file
        :param where_statement_params: parameters of where statements
        """

        if where_statement_params is None:
            where_statement_params = dict()
        where_statement = read_sql(
            sql_file=where_statement_file, **where_statement_params
        )
        sql = get_delete_sql(
            table_name=table_name,
            where_statement=where_statement,
        )
        with self.Session.begin() as session:
            session.execute(sql)

    def select_all(
        self,
        table_name: str,
        where_statement_file: str,
        where_statement_params: dict = None,
        return_type: str = "resultProxy",
    ):
        """
        Runs a select query on given table and returns the rows that conform where condition

        :param table_name: database table name
        :param where_statement_params: relative location of where statement sql file
        :param where_statement_file: parameters of where statements
        :param return_type: parameter which determines return type
        :return: iterable ResultProxy object that stores results of the select query
        """

        if where_statement_params is None:
            where_statement_params = dict()
        where_statement = read_sql(
            sql_file=where_statement_file, **where_statement_params
        )
        sql = get_select_all_sql(
            table_name=table_name,
            where_statement=where_statement,
        )

        with self.Session.begin() as session:
            if return_type == "dataframe":
                result = pd.read_sql(sql, session.bind)
            else:
                result = session.execute(sql).fetchall()
        return result

    def select(
        self,
        table_name: str,
        column_names: list,
        where_statement_file: str,
        where_statement_params: dict = None,
        return_type: str = "resultProxy",
    ):
        """
        Runs a select query on given table and returns the rows that conform where condition

        :param table_name: database table name
        :param column_names: column name from the table
        :param where_statement_params: relative location of where statement sql file
        :param where_statement_file: parameters of where statements
        :param return_type: parameter which determines return type
        :return: iterable ResultProxy object that stores results of the select query
        """

        if where_statement_params is None:
            where_statement_params = dict()
        where_statement = read_sql(
            sql_file=where_statement_file, **where_statement_params
        )
        sql = get_select_sql(
            table_name=table_name,
            column_names=column_names,
            where_statement=where_statement,
        )
        with self.Session.begin() as session:
            if return_type == "dataframe":
                result = pd.read_sql(sql, session.bind)
            else:
                result = session.execute(sql).fetchall()

        return result

    def get_row_count(
        self,
        table_name: str,
        where_statement_file: str = None,
        where_statement_params: dict = None,
    ):
        if where_statement_file is not None:
            if where_statement_params is None:
                where_statement_params = dict()
            where_statement = read_sql(
                sql_file=where_statement_file, **where_statement_params
            )
        else:
            where_statement = ""

        sql = get_row_count_sql(
            table_name=table_name,
            where_statement=where_statement,
        )
        with self.Session.begin() as session:
            cursor = session.execute(sql)
            row_count = cursor.fetchone()[0]
        return row_count

    def update(
        self,
        table_name: str,
        values: list,
    ):
        """
        Runs an update query on given table, and updates row columns that conform where condition if given

        :param table_name: database table name to write
        :param values: list of values as dictionary with the optional where statetment as a text
        exp: [{"values": [{"column": "column_name", "value": value_to_be_updated}],
            "where": "id = 1234"}]
        """

        update_util(table_name, values, self.Session)
