import gzip
from datetime import datetime
from typing import List, Iterable, Generator
from collections import defaultdict
import heapq
import itertools
import os

import requests

from src.model.pageview import Pageview
from src.utils import repeat_if_exception


class Wikimedia:
    """
    This class is responsible of downloading and computing the top 25 pageviews per domain.
    It tries to do so with the heavy use of generators instead of having all the pageviews in memory
    """

    PAGEVIEWS_URL_TEMPLATE = 'https://dumps.wikimedia.org/other/pageviews/{year}/{year}-{month}/pageviews-{date}-{hour}0000.gz'
    DIR_PATH = '/tmp'


    @classmethod
    @repeat_if_exception(message='Something went wrong when downloading the pagesviews data', nb_times=3)
    def get_pageviews(cls, dt: datetime) -> Generator['Pageview', None, None]:
        """ Get the pageviews data related to the datetime dt.
        it's a generator it doesn't load all the data in memory.
        It's getting one line a time from secondary storage and converts it to a Pageview instance

        :param dt: datetime of the request
        :return: gener
        """

        pageview_url = cls._get_pageview_url(dt)
        file_path = cls._download_file(pageview_url, dir_path=cls.DIR_PATH)

        for line in cls._read_lines(file_path):
            yield Pageview.instance_from_pageview_line(line)

        os.remove(file_path)


    @classmethod
    def _get_pageview_url(cls, dt: datetime) -> str :
        """ An internal method to compute the URL related to the datetime dt

        :param dt: datetime of the request
        :return: a URL to dt's pageview data
        """

        return cls.PAGEVIEWS_URL_TEMPLATE.format(year=dt.strftime('%Y'), month=dt.strftime('%m'),
                                                 date=dt.strftime('%Y%m%d'), hour=dt.strftime('%H'))


    @classmethod
    def _download_file(cls, url: str, dir_path: str, chunk_size=10 * 1024 ** 2) -> str:
        """ Downloads a file from url and saves it in a temporary path.

        :param url: url of the file to download
        :param dir_path: local path where to save the file
        :param chunk_size: the chunks we will download into RAM
        :return: file path of the downloaded file
        """

        file_name = url.split('/')[-1]
        file_path = os.path.join(dir_path, file_name)
        response = requests.get(url=url, stream=True)

        if response.status_code != requests.codes.ok:
           raise Exception(f'Something went wrong when downloading {url}')

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)

        return file_path


    @classmethod
    def _read_lines(cls, file_path: str) -> Generator[str, None, None]:
        """read lines of a gzipped file.

        :param file_path: path of the file to read
        :return: Generator over the lines of the file being read
        """

        with gzip.open(file_path, 'rt') as file_handle:
            yield from file_handle


    @classmethod
    def get_top_pageviews_per_domain(cls, pageviews: Iterable[Pageview], k=25) -> List[Pageview]:
        """ Get the top K pageviews per domain. The main data structure is a dictionary where each key
        represents a domain and each value is a min heap containing the top 25 pageviews based on the view_count
        of each pageview.
        Time complexity is O(n log k) where k is usually 25 and n number of elements in pageviews.

        :param pageviews: An iterable over a collection of pageviews
        :param k: The size of the min heap to compute top K pageviews per domain
        :return: Unsorted List of top K pageviews per domain
        """

        top_k_per_domain = defaultdict(list)

        for pageview in pageviews:
            domain, view_count = pageview.domain, pageview.view_count
            top_k = top_k_per_domain[domain]

            if len(top_k) < k:
                heapq.heappush(top_k, (view_count, id(pageview), pageview))

            elif len(top_k) == k and view_count > top_k[0][0]:
                heapq.heapreplace(top_k, (view_count, id(pageview), pageview))

        top_k_pageviews = list(pageview for _, _, pageview in itertools.chain(*top_k_per_domain.values()))

        return top_k_pageviews


    @classmethod
    def sort_pageviews_per_domain_and_views(cls, pageviews: List['Pageview']) -> None:
        """ Sort the pagviews per domain and view_count ascending. The sort is done in place.
        Time complexity is O(n log n)

        :param pageviews: list of pageviews to sort
        :return: None
        """

        pageviews.sort(key=lambda pageview: (pageview.domain, pageview.view_count))
