from typing import List, Callable, Any
from datetime import datetime, timedelta
import functools

import click


def get_yesterday_datetime_hour() -> str:
    yesterday_dt = datetime.now() - timedelta(days=1)
    return yesterday_dt.strftime('%Y%m%dT%H:00:00')


def get_datetime_hours_between(start_datetime: datetime, end_datetime: datetime = None) -> List[datetime]:
    if end_datetime is None:
        return [start_datetime]
    datetimes = []
    delta_hours = timedelta(hours=0)
    while start_datetime + delta_hours <= end_datetime:
        datetimes.append(start_datetime + delta_hours)
        delta_hours += timedelta(hours=1)
    return datetimes


def repeat_if_exception(message: str, nb_times: int = 3) -> Callable:

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
