import unittest
from unittest.mock import patch


from src.model.blacklist import BlackList


class BlacklistTest(unittest.TestCase):


    def test_get_pageviews_blacklist_failed(self):

        with patch('src.model.wikimedia.requests.get') as get_mock, \
             patch('click.echo'), \
             self.assertRaises(Exception):

            get_mock.return_value.status_code = 400
            BlackList.get_pageviews_blacklist()


    def test_get_pageviews_blacklist_success(self):
        pass
