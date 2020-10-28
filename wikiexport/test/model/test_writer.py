import unittest
from unittest.mock import patch, mock_open
from datetime import datetime

from src.model.pageview import Pageview
from src.model.writer import LocalWriter

class LocalWriterTest(unittest.TestCase):

    def test_write_pageviews_success(self):

        input_pageviews = [Pageview('a', 'main_page', 23), Pageview('b', 'second_page', 33)]
        output_dir_path = '/tmp/my-dir'
        dt = datetime(2020, 10, 23)
        header = 'domain,page_title,pageview_count'
        expected_lines = [f'{header}\n', 'a,main_page,23\n', 'b,second_page,33\n']
        expected_csv_path = '/tmp/my-dir/20201023T00:00:00.csv'

        with patch('src.model.writer.open', mock_open()) as open_mock:
            local_writer = LocalWriter(output_dir_path)
            actual_csv_path = local_writer.write_pageviews(input_pageviews, dt)

            open_mock.assert_called_once_with('/tmp/my-dir/20201023T00:00:00.csv', 'wt')
            file_handle = open_mock()
            actual_lines_written = [call.args[0] for call in file_handle.write.call_args_list]

            self.assertEqual(expected_lines, actual_lines_written)
            self.assertEqual(expected_csv_path, actual_csv_path)