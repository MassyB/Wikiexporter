import click

from src.utils import get_yesterday_datetime_hour, get_datetime_hours_between
from src.model.wikimedia import Wikimedia
from src.model.cache import LocalCache
from src.model.blacklist import BlackList
from src.model.writer import Writer

@click.command()

@click.option('--start-datetime',
              help='datetime (truncated to the hour) of the data to export. It\'s the start_date if end_date is specified',
              type=click.DateTime(formats=['%Y%m%dT%H:00:00']),
              default=get_yesterday_datetime_hour(), show_default = get_yesterday_datetime_hour() , required=True)

@click.option('--end-datetime',
              help='end datetime inclusive (truncated to the hour) of the range to export',
              type=click.DateTime(formats=['%Y%m%dT%H:00:00']))

@click.option('--output',
              help= 'output path where to put export files. Can be a directory or an S3 bucket of the form s3://mybucket/my-folder',
              type=click.STRING, required=True, default='/tmp')

@click.option('--aws-access-key-id', type=click.STRING, help='AWS credentials: ACCESS KEY ID')
@click.option('--aws-secret-access-key', type=click.STRING, help='AWS credentials: SECRET ACCESS KEY ID')

def main(start_datetime, end_datetime, output, aws_access_key_id, aws_secret_access_key):

    datetime_hours = get_datetime_hours_between(start_datetime, end_datetime)
    cache = LocalCache.get_instance()
    pageviews_blacklist = BlackList.get_pageviews_blacklist()
    writer = Writer.instantiate_writer(output, aws_access_key_id, aws_secret_access_key)

    for datetime_hour in datetime_hours:
        if datetime_hour not in cache:
            pageviews = Wikimedia.get_pageviews(datetime_hour)
            filtered_pageviews = (pageview for pageview in pageviews if pageview not in pageviews_blacklist)
            top_pageviews_per_domain = Wikimedia.get_top_pageviews_per_domain(filtered_pageviews)
            Wikimedia.sort_pageviews_per_domain_and_views(top_pageviews_per_domain)
            result_path = writer.write_pageviews(top_pageviews_per_domain, datetime_hour)
            cache.add_entry(datetime_hour, result_path)