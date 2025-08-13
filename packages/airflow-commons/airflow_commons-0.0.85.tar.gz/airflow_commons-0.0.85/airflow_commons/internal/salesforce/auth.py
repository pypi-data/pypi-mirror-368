import requests
from airflow_commons.internal.salesforce.http_utils import merge_path_parameters
from airflow_commons.internal.util.time_utils import datetime_add
from airflow_commons.logger import get_logger
from airflow_commons.internal.salesforce.constants import (
    GRANT_TYPE,
    AUTH_URL,
    TOKEN_PATH,
    V2,
    SERVICE_CLOUD_AUTH_URL,
    SERVICE_CLOUD_GRANT_TYPE,
    FORWARD_SLASH,
)
from datetime import datetime

from airflow_commons.resources.glossary import QUESTION_MARK


class Connection:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        account_id: str,
        subdomain: str,
        scope: str = None,
    ):
        """
        Creates a connection instance to salesforce marketing cloud API

        :param client_id: Account client id string
        :param client_secret: Account client secret
        :param account_id: Account id
        :param subdomain: Account specific subdomain
        :param scope: Authorization scope
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.account_id = account_id
        self.auth_url = AUTH_URL.format(subdomain=subdomain)
        self.scope = scope
        self.logger = get_logger("Connection")
        self._authenticate()

    def _authenticate(self):
        """
        Authenticates to salesforce marketing cloud
        :return:
        """
        body = {
            "grant_type": GRANT_TYPE,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "account_id": self.account_id,
        }
        if self.scope is not None:
            body["scope"] = self.scope
        now = datetime.now()
        auth_response = requests.post(
            url=(self.auth_url + merge_path_parameters(V2, TOKEN_PATH)), json=body
        )
        try:
            auth_response.raise_for_status()
        except Exception as e:
            if auth_response:
                self.logger.error(
                    "An error occured during authentication " + auth_response.text
                )
            raise Exception(str(e)) from e
        auth_response_json = auth_response.json()
        self.access_token = auth_response_json["access_token"]
        self.token_expiration_period = auth_response_json["expires_in"] - 60
        self.soap_instance_url = auth_response_json["soap_instance_url"]
        self.rest_instance_url = auth_response_json["rest_instance_url"]
        self.token_expiration_at = datetime_add(
            now, seconds=self.token_expiration_period
        )

    def check_and_refresh_token(self):
        """
        Checks if current token is expired, if so re-authenticates itself.
        :return:
        """
        now = datetime.now()
        if now > self.token_expiration_at:
            return
        self._authenticate()


class SalesCloudConnection:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        subdomain: str,
        scope: str = None,
    ):
        """
        Creates a connection instance to salesforce service cloud API

        :param client_id: Account client id string
        :param client_secret: Account client secret
        :param subdomain: Authentication prefix for environment
        :param refresh_token: Refresh token
        :param scope: Authorization scope
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.auth_url = SERVICE_CLOUD_AUTH_URL.format(subdomain=subdomain)
        self.scope = scope
        self.logger = get_logger("Connection")
        self._authenticate()

    def _authenticate(self):
        """
        Authenticates to salesforce sales cloud
        :return:
        """
        body = {
            "grant_type": SERVICE_CLOUD_GRANT_TYPE,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if self.scope is not None:
            body["scope"] = self.scope
        auth_url_extension = (
            f"grant_type={SERVICE_CLOUD_GRANT_TYPE}&client_id={self.client_id}"
            f"&client_secret={self.client_secret}&refresh_token={self.refresh_token}"
        )
        auth_response = requests.post(
            url=(
                self.auth_url
                + FORWARD_SLASH
                + TOKEN_PATH
                + QUESTION_MARK
                + auth_url_extension
            )
        )
        try:
            auth_response.raise_for_status()
        except Exception as e:
            if auth_response:
                self.logger.error(
                    "An error occured during authentication " + auth_response.text
                )
            raise Exception(str(e)) from e

        auth_response_json = auth_response.json()
        self.access_token = auth_response_json["access_token"]
        self.signature = auth_response_json["signature"]
        self.scope = auth_response_json["scope"]
        self.instance_url = auth_response_json["instance_url"]
        self.id = auth_response_json["id"]
        self.token_type = auth_response_json["token_type"]
        self.token_expiration_at = datetime_add(
            datetime.fromtimestamp(int(auth_response_json["issued_at"]) / 1000),
            minutes=25,
        )

    def check_and_refresh_token(self):
        """
        Checks if current token is expired, if so re-authenticates itself.
        :return:
        """
        now = datetime.now()
        if now > self.token_expiration_at:
            return
        self._authenticate()
