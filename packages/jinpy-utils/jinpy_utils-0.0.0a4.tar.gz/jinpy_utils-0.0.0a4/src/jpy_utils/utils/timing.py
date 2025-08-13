from datetime import UTC, datetime


def get_current_datetime() -> datetime:
    """This function will return timezone aware datetime obj"""
    return datetime.now(UTC)
