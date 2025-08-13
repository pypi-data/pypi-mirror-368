import requests
import threading
from datetime import datetime
from airflow_commons.internal.salesforce.constants import (
    DATA_PATH,
    UPSERT_ACCOUNT_PATH,
    UPDATE_ACCOUNT_PATH,
    QUERY_PATH,
)
from airflow_commons.internal.util.time_utils import get_interval_duration
from airflow_commons.internal.salesforce.auth import Connection, SalesCloudConnection
from airflow_commons.internal.salesforce.http_utils import (
    get_headers,
    get_async_operation_url,
    get_async_operation_result_url,
    get_async_operation_status_url,
    get_sync_operation_url,
    get_fetch_operation_url,
)
from airflow_commons.internal.salesforce.defaults import (
    TIMEOUT,
)
from airflow_commons.logger import get_logger


class SalesForceOperator(object):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        account_id: str,
        subdomain: str,
        scope: str = None,
        timeout: int = TIMEOUT,
    ):
        """
        Initializes SalesForceOperator instance with given parameters.
        If no scope is provided, connection starts with every operation available.

        :param client_id: Account client id string
        :param client_secret: Account client secret
        :param account_id: Account id
        :param subdomain: Account specific subdomain
        :param scope: Authorization scope, default value is None
        :param timeout: request timeout duration parameter
        """
        self.logger = get_logger("SalesForceOperator")
        self.connection = Connection(
            client_id=client_id,
            client_secret=client_secret,
            account_id=account_id,
            subdomain=subdomain,
            scope=scope,
        )
        self.session = requests.Session()
        self.timeout = timeout
        self.lock = threading.Lock()

    def async_upsert(self, key: str, data):
        """
        Starts an async upsert of given data to the data extension provided by key.
        :param key: External customer key of the data extension
        :param data: Data to be uploaded as json array
        :return:
        """
        return self._async_operation(key=key, data=data, method="PUT")

    def async_insert(self, key: str, data):
        """
        Starts an async insert of given data to the data extension provided by key.
        :param key: External customer key of the data extension
        :param data: Data to be uploaded as json array
        :return:
        """
        return self._async_operation(key=key, data=data, method="POST")

    def get_async_operation_result(self, request_id: str):
        """
        Returns result of an ongoing async process.
        :param request_id: ID of async request, can be found in the response of async request itself.
        :return:
        """
        url = get_async_operation_result_url(
            base_url=self.connection.rest_instance_url, request_id=request_id
        )
        request = requests.Request(
            method="GET",
            url=url,
            headers=get_headers(access_token=self.connection.access_token),
        )
        prep = request.prepare()
        return self.session.send(prep, timeout=self.timeout)

    def get_async_operation_status(self, request_id: str):
        """
        Returns current status of an ongoing async process.
        :param request_id: ID of async request, can be found in the response of async request itself.
        :return:
        """
        url = get_async_operation_status_url(
            base_url=self.connection.rest_instance_url, request_id=request_id
        )
        request = requests.Request(
            method="GET",
            url=url,
            headers=get_headers(access_token=self.connection.access_token),
        )
        prep = request.prepare()
        return self.session.send(prep, timeout=self.timeout)

    def _async_operation(self, key: str, data, method: str):
        """
        Internal method of async upsert and insert operations.
        :param key: External customer key of the data extension
        :param data: Data to be uploaded as json array
        :param method: HTTP method
        :return:
        """
        start = datetime.now()
        self.connection.check_and_refresh_token()
        url = get_async_operation_url(
            base_url=self.connection.rest_instance_url, key=key
        )
        request = requests.Request(
            method=method,
            url=url,
            json=data,
            headers=get_headers(access_token=self.connection.access_token),
        )
        prep = request.prepare()
        response = self.session.send(prep, timeout=self.timeout)
        try:
            response.raise_for_status()
            end = datetime.now()
            self.logger.debug(
                f"Async operation finished in {get_interval_duration(start, end)} seconds"
            )
        except Exception as e:
            if response:
                self.logger.error(
                    "An error occurred during async operation, "
                    + str(e)
                    + ", response from Salesforce "
                    + response.text
                )
        return response

    def sync_upsert(self, key: str, data):
        """
        Sync upsert of given data to the data extension provided by key.
        :param key: External customer key of the data extension
        :param data: Data to be uploaded as json array
        :return:
        """
        start = datetime.now()
        self.connection.check_and_refresh_token()
        url = get_sync_operation_url(
            base_url=self.connection.rest_instance_url, key=key
        )
        request = requests.Request(
            method="POST",
            url=url,
            json=data,
            headers=get_headers(access_token=self.connection.access_token),
        )
        prep = request.prepare()
        response = self.session.send(prep, timeout=self.timeout)
        try:
            response.raise_for_status()
            end = datetime.now()
            self.logger.debug(
                f"Sync operation finished in {get_interval_duration(start, end)} seconds"
            )
        except Exception as e:
            if response:
                self.logger.error(
                    "An error occurred during sync operation, "
                    + str(e)
                    + ", response from Salesforce "
                    + response.text
                )
        return response

    def sync_fetch(self, key: str, filter: str = None):
        """
        Sync upsert of given data to the data extension provided by key.
        :param key: External customer key of the data extension
        :param filter: Filter to apply to data extension search
        :return:
        """
        start = datetime.now()
        self.connection.check_and_refresh_token()
        url = get_fetch_operation_url(
            base_url=self.connection.rest_instance_url, key=key, filter=filter
        )
        request = requests.Request(
            method="GET",
            url=url,
            headers=get_headers(access_token=self.connection.access_token),
        )
        prep = request.prepare()
        response = self.session.send(prep, timeout=self.timeout)
        try:
            response.raise_for_status()
            end = datetime.now()
            self.logger.debug(
                f"Sync operation finished in {get_interval_duration(start, end)} seconds"
            )
        except Exception as e:
            if response:
                self.logger.error(
                    "An error occurred during sync operation, "
                    + str(e)
                    + ", response from Salesforce "
                    + response.text
                )
        return response

    def check_and_refresh(self):
        return self.connection.check_and_refresh_token()

    def get_next_page(self, next: str, timeout: int = TIMEOUT):
        """
        Creates request url and gets next page response
        :param next: Next page endpoint of previous page
        :param timeout: send request timeout duration in second, default is 30
        :return: requests.Response
        """
        self.connection.check_and_refresh_token()
        request_url = self.connection.rest_instance_url + DATA_PATH + next
        request = requests.Request(
            method="GET",
            url=request_url,
            headers=get_headers(access_token=self.connection.access_token),
        )
        return self.session.send(request.prepare(), timeout=timeout)


class SalesCloudOperator(object):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        subdomain: str,
        scope: str = None,
        timeout: int = TIMEOUT,
    ):
        """
        Initializes SalesCloudOperator instance with given parameters.
        If no scope is provided, connection starts with every operation available.

        :param client_id: Account client id string
        :param client_secret: Account client secret
        :param refresh_token: Account refresh token
        :param subdomain: Authentication prefix for environment
        :param scope: Authorization scope, default value is None
        :param timeout: request timeout duration parameter
        """
        self.logger = get_logger("SalesCloudOperator")
        self.connection = SalesCloudConnection(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            subdomain=subdomain,
            scope=scope,
        )
        self.session = requests.Session()
        self.timeout = timeout

    def upsert_account(self, data):
        """
        Sync upsert of given data to the data extension provided by key.
        :param data: Data to be uploaded as json array
        :return:
        """
        start = datetime.now()
        self.connection.check_and_refresh_token()
        request = requests.Request(
            method="POST",
            url=self.connection.instance_url + UPSERT_ACCOUNT_PATH,
            json=data,
            headers=get_headers(access_token=self.connection.access_token),
        )
        prep = request.prepare()
        response = self.session.send(prep, timeout=self.timeout)
        try:
            response.raise_for_status()
            end = datetime.now()
            self.logger.debug(
                f"Sync operation finished in {get_interval_duration(start, end)} seconds"
            )
        except Exception as e:
            if response:
                self.logger.error(
                    "An error occurred during sync operation, "
                    + str(e)
                    + ", response from Salesforce "
                    + response.text
                )
        return response

    def update_account(self, data):
        """
        Sync update of given data to the data extension provided by key.
        :param data: Data to be uploaded as json array
        :return:
        """
        start = datetime.now()
        self.connection.check_and_refresh_token()
        request = requests.Request(
            method="POST",
            url=self.connection.instance_url + UPDATE_ACCOUNT_PATH,
            json=data,
            headers=get_headers(access_token=self.connection.access_token),
        )
        prep = request.prepare()
        response = self.session.send(prep, timeout=self.timeout)
        try:
            response.raise_for_status()
            end = datetime.now()
            self.logger.debug(
                f"Sync operation finished in {get_interval_duration(start, end)} seconds"
            )
        except Exception as e:
            if response:
                self.logger.error(
                    "An error occurred during sync operation, "
                    + str(e)
                    + ", response from Salesforce "
                    + response.text
                )
        return response

    def get_query_results(self, query):
        """
        Returns the results of the given query.
        :param query: SoqlQuery string
        :return:
        """
        start = datetime.now()
        self.connection.check_and_refresh_token()
        request = requests.Request(
            method="GET",
            url=self.connection.instance_url + QUERY_PATH + query,
            headers=get_headers(access_token=self.connection.access_token),
        )
        prep = request.prepare()
        response = self.session.send(prep, timeout=self.timeout)
        try:
            response.raise_for_status()
            end = datetime.now()
            self.logger.debug(
                f"Get SOQL query results finished in {get_interval_duration(start, end)} seconds"
            )
        except Exception as e:
            if response:
                self.logger.error(
                    "An error occurred during SOQL query operation, "
                    + str(e)
                    + ", response from Salesforce "
                    + response.text
                )
        return response
