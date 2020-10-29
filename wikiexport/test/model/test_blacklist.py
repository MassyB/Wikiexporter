import unittest
from unittest.mock import patch


from src.model.blacklist import BlackList

from requests import codes

from wikiexport.src.model.pageview import Pageview


class BlacklistTest(unittest.TestCase):


    def test_get_pageviews_blacklist_failed(self):

        with patch('src.model.wikimedia.requests.get') as get_mock, \
             patch('click.echo'), \
             self.assertRaises(Exception):

            get_mock.return_value.status_code = 400
            BlackList.get_pageviews_blacklist()


    def test_get_pageviews_blacklist_success(self):

        expected_pageviews = {Pageview('a', 'main_page', None), Pageview('b', 'second_page', None)}

        with patch('src.model.wikimedia.requests.get') as get_mock:
            get_mock.return_value.status_code = codes.ok
            get_mock.return_value.iter_lines = lambda : ('a main_page', 'b second_page')

            actual_pageviews = BlackList.get_pageviews_blacklist()
            self.assertEqual(expected_pageviews, actual_pageviews)
