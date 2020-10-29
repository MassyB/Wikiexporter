import unittest
from unittest.mock import patch

from src.utils import get_yesterday_datetime_hour, get_datetime_hours_between
from datetime import datetime


class TestUtils(unittest.TestCase):


    def test_get_yesterday_datetime_hour(self):

        with patch('src.utils.datetime') as mocked_datetime:

            mocked_datetime.now.return_value = datetime(2020, 1, 2, 23, 56, 23)
            expected_yesterday = '20200101T23:00:00'
            actual_yesterday_hour = get_yesterday_datetime_hour()

        self.assertEqual(expected_yesterday, actual_yesterday_hour)


    def test_get_datetime_hours_between_two_datetime_hours(self):

        start_datetime = datetime(2020, 1, 2, 23)
        end_datetime = datetime(2020, 1, 3, 3)

        expected_hours = [datetime(2020, 1, 2, 23), datetime(2020, 1, 3, 0), datetime(2020, 1, 3, 1),
                          datetime(2020, 1, 3, 2), datetime(2020, 1, 3, 3)]

        actual_hours = get_datetime_hours_between(start_datetime, end_datetime)

        self.assertEqual(expected_hours, actual_hours)


    def test_datetime_hours_between_two_datetime_hours_end_datetime_none(self):

        start_datetime = datetime(2020, 1, 2, 23)
        end_datetime = None

        expected_hours = [start_datetime]

        actual_hours = get_datetime_hours_between(start_datetime, end_datetime)

        self.assertEqual(expected_hours, actual_hours)
