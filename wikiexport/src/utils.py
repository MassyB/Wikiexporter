from typing import List, Callable, Any
from datetime import datetime, timedelta
import functools

import click


def get_yesterday_datetime_hour() -> str:
    """ Computes yesterdays - 24 hours datetime truncated to the hour

    :return: datetime in %Y%m%dT%H:00:00 format
    """

    yesterday_dt = datetime.now() - timedelta(days=1)

    return yesterday_dt.strftime('%Y%m%dT%H:00:00')


def get_datetime_hours_between(start_datetime: datetime, end_datetime: datetime = None) -> List[datetime]:
    """ Computes the hours in %Y%m%dT%H:00:00 format between two datetimes

    :param start_datetime:
    :param end_datetime:
    :return: hours between start_datetime and end_datetime inclusive
    """

    if end_datetime is None:
        return [start_datetime]
    datetimes = []
    delta_hours = timedelta(hours=0)
    while start_datetime + delta_hours <= end_datetime:
        datetimes.append(start_datetime + delta_hours)
        delta_hours += timedelta(hours=1)

    return datetimes


def repeat_if_exception(message: str, nb_times: int = 3) -> Callable:
    """ A decorator that repeats a function if it raises some exception

    :param message: A message to print when an exception occures during the execution of the decorated function
    :param nb_times: Number of time to execute the function
    :return: a decorator to apply on functions
    """

    def repeat_decorator(func: Callable ) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:

            for i in range(nb_times - 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    click.echo(click.style(message, fg='red'))
                    click.echo(click.style(f'Exception {type(e)} occurred with arguments: {e.args}', fg='red'))
                    click.echo(f'Trying once again. {nb_times - (i + 1)} retries remaining')

            return func(*args, **kwargs)

        return wrapper

    return repeat_decorator
