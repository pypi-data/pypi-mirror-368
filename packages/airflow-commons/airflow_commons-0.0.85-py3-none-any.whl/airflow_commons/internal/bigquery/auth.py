import json

from google.cloud import bigquery


def connect(service_account_file: str, service_account_str: str):
    """
    Connects to Bigquery client with given service account file path or string service account.

    :param service_account_file: relative location of service account json
    :param service_account_str: The string credential with a private key and other credentials information
    :return: a Client object instance required for API requests
    :raises: AssertionError: If there is no given service account
    """
    assert not (
        service_account_file is None and service_account_str is None
    ), "No service account has been provided"
    if service_account_str:
        info = json.loads(service_account_str)
        return bigquery.Client.from_service_account_info(info)
    return bigquery.Client.from_service_account_json(service_account_file)
