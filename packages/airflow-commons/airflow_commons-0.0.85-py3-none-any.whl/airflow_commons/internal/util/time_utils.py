from datetime import datetime, timedelta

BUFFER_DURATION_IN_MINUTES = 10


def get_buffered_timestamp(timestamp: str, buffer_duration=BUFFER_DURATION_IN_MINUTES):
    """
    Adds ten minutes buffer to given start date

    :param timestamp: start date
    :param buffer_duration: buffer duration in minutes
    :return: buffered start date
    """
    start = datetime_subtract(
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"), minutes=buffer_duration
    )
    return start.strftime("%Y-%m-%d %H:%M:%S")


def get_interval_duration(start: datetime, end: datetime):
    """
    Calculates duration between two datetimes

    :param start: timer start parameter
    :param end: timer end parameter
    :return:
    """
    return round((end - start).total_seconds())


def datetime_add(timestamp: datetime, seconds: int = None, minutes: int = None):
    if seconds is not None:
        return timestamp + timedelta(seconds=seconds)
    if minutes is not None:
        return timestamp + timedelta(minutes=minutes)


def datetime_subtract(timestamp: datetime, seconds: int = None, minutes: int = None):
    if seconds is not None:
        return timestamp - timedelta(seconds=seconds)
    if minutes is not None:
        return timestamp - timedelta(minutes=minutes)
