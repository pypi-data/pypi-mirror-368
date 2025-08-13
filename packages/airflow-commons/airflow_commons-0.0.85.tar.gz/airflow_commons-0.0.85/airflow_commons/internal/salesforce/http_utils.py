from airflow_commons.internal.salesforce.constants import (
    ASYNC_PATH,
    DATA_EXTENSION_KEY_PATH,
    ASYNC_JOB_RESULT_PATH,
    ASYNC_JOB_STATUS_PATH,
    DATA_PATH,
    CUSTOM_OBJECT_DATA_PATH,
    FILTER_QUERY,
    SYNC_PATH,
    DATA_EVENT_KEY_PATH,
    FORWARD_SLASH,
    V1,
)
from airflow_commons.resources.glossary import QUESTION_MARK


def get_headers(access_token: str):
    """
    Builds a request header with given token.
    :param access_token: Active access token
    :return:
    """
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }


def get_async_operation_url(base_url: str, key: str):
    """
    Builds an async operation url
    :param base_url:
    :param key:
    :return:
    """
    return (
        base_url
        + merge_path_parameters(DATA_PATH, V1, ASYNC_PATH)
        + DATA_EXTENSION_KEY_PATH.format(key=key)
    )


def get_async_operation_result_url(base_url: str, request_id: str):
    """
    Builds an async operation result url
    :param base_url:
    :param request_id:
    :return:
    """
    return (
        base_url
        + merge_path_parameters(DATA_PATH, V1, ASYNC_PATH)
        + ASYNC_JOB_RESULT_PATH.format(request_id=request_id)
    )


def get_async_operation_status_url(base_url: str, request_id: str):
    """
    Builds an async operation status url
    :param base_url:
    :param request_id:
    :return:
    """
    return (
        base_url
        + merge_path_parameters(DATA_PATH, V1, ASYNC_PATH)
        + ASYNC_JOB_STATUS_PATH.format(request_id=request_id)
    )


def get_fetch_operation_url(base_url: str, key: str, filter: str = None):
    """
    Builds a get operation url
    :param base_url:
    :param key:
    :param filter: optional filter of search query
    :return:
    """
    url = (
        base_url
        + merge_path_parameters(DATA_PATH, V1)
        + CUSTOM_OBJECT_DATA_PATH.format(key=key)
    )
    if filter:
        url = url + QUESTION_MARK + FILTER_QUERY.format(filter=filter)

    return url


def get_sync_operation_url(base_url: str, key: str):
    """
    Builds a sync operation url
    :param base_url:
    :param key:
    :return:
    """
    return (
        base_url
        + merge_path_parameters(SYNC_PATH, V1)
        + DATA_EVENT_KEY_PATH.format(key=key)
    )


def merge_path_parameters(*parameters: str):
    """
    Builds merged endpoint with given sequential parameters using forward slash
    :param parameters: String endpoint parameters
    :raises: AssertionError: If parameter count is not more than one
    :return: Merged endpoint as string
    """
    assert len(parameters) > 1, "Parameters must be more than one"
    return FORWARD_SLASH.join(parameters)
