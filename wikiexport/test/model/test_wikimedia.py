import unittest
from unittest.mock import patch, mock_open
from requests import codes

from src.model.wikimedia import Wikimedia
from src.model.pageview import Pageview

class WikimediaTest(unittest.TestCase):


    def test_get_top_3_pageviews_per_domain(self):

        pageviews = [# domain a
                     Pageview(domain='a', page_title='page1', view_count=12),
                     Pageview(domain='a', page_title='page2', view_count=10),
                     Pageview(domain='a', page_title='page3', view_count=1),
                     Pageview(domain='a', page_title='page4', view_count=3),
                     Pageview(domain='a', page_title='page5', view_count=33),
                     # domain ab
                     Pageview(domain='ab', page_title='page1', view_count=12),
                     Pageview(domain='ab', page_title='page2', view_count=33),
                     Pageview(domain='ab', page_title='page3', view_count=2),
                     # domaine ab.c
                     Pageview(domain='ab.c', page_title='page1', view_count=44),
                     Pageview(domain='ab.c', page_title='page2', view_count=33),
                     Pageview(domain='ab.c', page_title='page3', view_count=22),
                     Pageview(domain='ab.c', page_title='page5', view_count=33)]


        expected_top_3_pageviews = {# domain a
                                    Pageview(domain='a', page_title='page1', view_count=12),
                                    Pageview(domain='a', page_title='page5', view_count=33),
                                    Pageview(domain='a', page_title='page2', view_count=10),
                                    # domain b
                                    Pageview(domain='ab', page_title='page1', view_count=12),
                                    Pageview(domain='ab', page_title='page2', view_count=33),
                                    Pageview(domain='ab', page_title='page3', view_count=2),
                                    # domain ab.c
                                    Pageview(domain='ab.c', page_title='page1', view_count=44),
                                    Pageview(domain='ab.c', page_title='page2', view_count=33),
                                    Pageview(domain='ab.c', page_title='page5', view_count=33)}


        actual_top_3_pageviews = set(Wikimedia.get_top_pageviews_per_domain(pageviews, k=3))

        self.assertEqual(expected_top_3_pageviews, actual_top_3_pageviews)


    def test_sort_pageviews_per_domain_and_view_count(self):

        pageviews = [Pageview(domain='ab', page_title='page2', view_count=33),
                     Pageview(domain='a', page_title='page1', view_count=12),
                     Pageview(domain='ab.c', page_title='page2', view_count=33),
                     Pageview(domain='ab', page_title='page1', view_count=12),
                     Pageview(domain='ab.c', page_title='page1', view_count=44),
                     Pageview(domain='ab.c', page_title='page5', view_count=33)]

        expected_sorted_pageviews = [Pageview(domain='a', page_title='page1', view_count=12),
                                     Pageview(domain='ab', page_title='page1', view_count=12),
                                     Pageview(domain='ab', page_title='page2', view_count=33),
                                     Pageview(domain='ab.c', page_title='page2', view_count=33),
                                     Pageview(domain='ab.c', page_title='page5', view_count=33),
                                     Pageview(domain='ab.c', page_title='page1', view_count=44)]

        Wikimedia.sort_pageviews_per_domain_and_views(pageviews)


        self.assertEqual(expected_sorted_pageviews, pageviews)


    def test_download_url_success(self):

        url = 'https://dumps.wikimedia.org/other/pageviews/2020/2020-01/pageviews-20200101-010000.gz'
        dir = Wikimedia.DIR_PATH
        expected_file_path = f'{dir}/pageviews-20200101-010000.gz'

        with patch('src.model.wikimedia.open', new=mock_open()) as open_mock, \
             patch('src.model.wikimedia.requests.get') as get_mock:

            get_mock.return_value.status_code = codes.ok
            actual_file_path = Wikimedia._download_file(url, dir)

            open_mock.assert_called_once_with(expected_file_path, 'wb')
            self.assertEqual(expected_file_path, actual_file_path)


    def test_download_url_failed(self):

        url = 'https://dumps.wikimedia.org/other/pageviews/2020/2020-01/pageviews-20200101-010000.gz'
        dir = Wikimedia.DIR_PATH

        with patch('src.model.wikimedia.requests.get') as get_mock, \
             self.assertRaises(Exception):

            get_mock.return_value.status_code = 400
            Wikimedia._download_file(url, dir)
