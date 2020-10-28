from typing import Set

from src.model.pageview import Pageview
from src.utils import repeat_if_exception


import requests


class BlackList:
    BLACKLIST_URL = 'https://s3.amazonaws.com/dd-interview-data/data_engineer/wikipedia/blacklist_domains_and_pages'
    PAGEVIEWS_BLACKLIST = set()

    @classmethod
    @repeat_if_exception(message='Something went wrong when downloading the pageviews blacklist from S3')
    def get_pageviews_blacklist(cls) -> Set[str]:
        if not cls.PAGEVIEWS_BLACKLIST:
            response = requests.get(cls.BLACKLIST_URL, stream=True)
            if response.status_code != requests.codes.ok:
                raise Exception('Black list could not be downloaded')
            for line in response.iter_lines():
                pageview = Pageview.instance_from_balcklist(str(line))
                cls.PAGEVIEWS_BLACKLIST.add(pageview)

        return cls.PAGEVIEWS_BLACKLIST