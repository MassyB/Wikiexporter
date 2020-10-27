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
    PAGEVIEWS_URL_TEMPLATE = 'https://dumps.wikimedia.org/other/pageviews/{year}/{year}-{month}/pageviews-{date}-{hour}0000.gz'
    DIR_PATH = '/tmp'

    @classmethod
    @repeat_if_exception(message='Something went wrong when downloading the pagesviews data', nb_times=3)
    def get_pageviews(cls, dt: datetime) -> Generator['Pageview', None, None]:
        pageview_url = cls._get_pageview_url(dt)
        file_path = cls._download_file(pageview_url, dir_path=cls.DIR_PATH)
        for line in cls._read_lines(file_path):
            yield Pageview.instance_from_pageview_line(line)
        #todo remove file

    @classmethod
    def _get_pageview_url(cls, dt: datetime) -> str :
        return cls.PAGEVIEWS_URL_TEMPLATE.format(year=dt.strftime('%Y'), month=dt.strftime('%m'),
                                                 date=dt.strftime('%Y%m%d'), hour=dt.strftime('%H'))

    @classmethod
    def _download_file(cls, url: str, dir_path: str, chunk_size=10 * 1024 ** 2) -> str:
        """Downloads a file from url and saves it in path.

        :param url: url of the file to download
        :param dir_path: local path where to save the file
        :param chunk_size: the chunks we will download into RAM
        :return: None
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

        :param file_path:
        :return: Iterable[str] lines of the gzipped file
        """

        with gzip.open(file_path, 'rt') as file_handle:
            yield from file_handle

    @classmethod
    def get_top_pageviews_per_domain(cls, pageviews: Iterable[Pageview], k=25) -> List[Pageview]:
        """get the top 25 pages view per domain. use heaps to get

        :param pageviews:
        :param k:
        :return:
        """

        top_k_per_domain = defaultdict(lambda: list())

        for pageview in pageviews:
            domain, view_count = pageview.domain, pageview.view_count
            top_k = top_k_per_domain[domain]

            if len(top_k) < k:
                heapq.heappush(top_k, (view_count, id(pageview), pageview))

            elif len(top_k) == k and view_count > top_k[0][0]:
                heapq.heapreplace(top_k, (view_count, id(pageview), pageview))

        top_k_pageviews = list(pageview for _, _, pageview in  itertools.chain(*top_k_per_domain.values()))
        return top_k_pageviews

    @classmethod
    def sort_pageviews_per_domain_and_views(cls, pageviews: List['Pageview']) -> None:
        pageviews.sort(key=lambda pageview: (pageview.domain, pageview.view_count))