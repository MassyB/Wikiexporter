from unittest import TestCase
from unittest.mock import patch, mock_open
from datetime import datetime


from src.model.cache import LocalCache


class LocalCacheTest(TestCase):


    def setUp(self):

        LocalCache._remove_instance()


    def test_instantiated_once(self):

        file_path_to_open = LocalCache.CACHE_FILE_PATH

        with patch('src.model.cache.open', new=mock_open()) as open_mock,\
             self.assertRaises(Exception):

             LocalCache.get_instance()
             open_mock.assert_called_once_with(file_path_to_open, 'a+')
             LocalCache()


    def test_equal_instances(self):

        with patch('src.model.cache.open', new=mock_open()):
            first_instance = LocalCache.get_instance()
            second_instance = LocalCache.get_instance()

            self.assertEqual(first_instance, second_instance)


    def test_initialization_of_cache(self):

        file_content = '\n'.join(['20200101T01:00:00,tmp/pageviews-2020010T01:00:00.csv',
                                  '20200102T01:00:00,s3://datadog/de/pageviews-20200102T01:00:00.csv'])

        with patch('src.model.cache.open', new=mock_open(read_data=file_content)):
            local_cache = LocalCache.get_instance()
            expected_cache = {datetime(2020, 1, 1, 1): 'tmp/pageviews-2020010T01:00:00.csv',
                              datetime(2020, 1, 2, 1): 's3://datadog/de/pageviews-20200102T01:00:00.csv'}

            self.assertEqual(local_cache.cache, expected_cache)

    def test_cache_hit(self):

        file_content = '\n'.join(['20200101T01:00:00,tmp/pageviews-2020010T01:00:00.csv',
                                  '20200102T01:00:00,s3://datadog/de/pageviews-20200102T01:00:00.csv'])
        expected_value = 'tmp/pageviews-2020010T01:00:00.csv'

        with patch('src.model.cache.open', new=mock_open(read_data=file_content)):
            local_cache = LocalCache.get_instance()

            self.assertEqual(local_cache.get_entry(datetime(2020, 1, 1, 1)), expected_value)


    def test_cache_miss(self):

        file_content = '\n'.join(['20200101T01:00:00,tmp/pageviews-2020010T01:00:00.csv',
                                  '20200102T01:00:00,s3://datadog/de/pageviews-20200102T01:00:00.csv'])
        expected_value = None
        with patch('src.model.cache.open', new=mock_open(read_data=file_content)):
            local_cache = LocalCache.get_instance()

            self.assertEqual(local_cache.get_entry(datetime(2020, 1, 3, 1)), expected_value)
