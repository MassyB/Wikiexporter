from typing import Set

from src.model.pageview import Pageview
from src.utils import repeat_if_exception


import requests


class BlackList:
    """
    Class that downloads, only once, blacklisted pageviews and saves them in a class attribute
    """

    BLACKLIST_URL = 'https://s3.amazonaws.com/dd-interview-data/data_engineer/wikipedia/blacklist_domains_and_pages'
    PAGEVIEWS_BLACKLIST = set()

    @classmethod
    @repeat_if_exception(message='Something went wrong when downloading the pageviews blacklist from S3')
    def get_pageviews_blacklist(cls) -> Set['Pageview']:
        """Downloads, only once, a set of pagesviews from the BALCKLIST_URL and saves that in a set.
        If the the pageview were already downloaded, simply return the class attribute

        :return: Set of pagesviews to filter out
        """

        if not cls.PAGEVIEWS_BLACKLIST:
            response = requests.get(cls.BLACKLIST_URL, stream=True)
            if response.status_code != requests.codes.ok:
                raise Exception('Black list could not be downloaded')
            for line in response.iter_lines():
                pageview = Pageview.instance_from_balcklist(str(line))
                cls.PAGEVIEWS_BLACKLIST.add(pageview)

        return cls.PAGEVIEWS_BLACKLIST
