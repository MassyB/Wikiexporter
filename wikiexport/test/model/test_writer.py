import unittest
from unittest.mock import patch, mock_open
from datetime import datetime

from src.model.pageview import Pageview
from src.model.writer import LocalWriter, S3Writer

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


    def test_write_pageviews_failed(self):

        input_pageviews = [Pageview('a', 'main_page', 23)]
        output_dir_path = '/tmp/a-dir/that/doesnt/exist'
        dt = datetime(2020, 10, 23)

        with patch('src.model.writer.open', mock_open()) as open_mock, \
             patch('click.echo'), \
             self.assertRaises(FileNotFoundError):

            open_mock.side_effect = FileNotFoundError()
            LocalWriter(output_dir_path).write_pageviews(input_pageviews, dt)
            open_mock.assert_called_once_with('/tmp/a-dir/that/doesnt/exist/20201023T00:00:00.csv', 'wt')


class S3WriterTest(unittest.TestCase):


    def test_get_bucket_and_object(self):

        dt = datetime(2020, 10, 27)
        with patch('boto3.Session'):
            s3_writer = S3Writer('s3://my-bucket/my/directory', None, None)
            self.assertEqual(s3_writer._get_bucket_and_object(dt), ('my-bucket', 'my/directory/20201027T00:00:00.csv'))

            s3_writer = S3Writer('s3://my-bucket/my/second-directory/', None, None)
            self.assertEqual(s3_writer._get_bucket_and_object(dt), ('my-bucket', 'my/second-directory/20201027T00:00:00.csv'))
