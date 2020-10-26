from typing import List
from datetime import datetime, timedelta


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