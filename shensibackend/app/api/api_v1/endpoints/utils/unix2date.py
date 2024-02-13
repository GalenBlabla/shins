from datetime import datetime


def timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Convert a Unix timestamp to a Python datetime object.

    :param timestamp: Unix timestamp
    :return: datetime object
    """
    # Convert the Unix timestamp to seconds (assuming the timestamp is in milliseconds)
    if timestamp > 9999999999:  # This checks if the timestamp is in milliseconds
        timestamp = timestamp / 1000

    # Convert to datetime
    return datetime.fromtimestamp(timestamp)
