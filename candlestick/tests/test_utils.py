from datetime import datetime, date
from candlestick.utils import *

from unittest import TestCase

class TimestampToDatetimeTests(TestCase):

    def test_naive_datetime(self):
        self.assertEqual(
            timestamp_to_datetime(1222624800, None, "H"),
            datetime(2008, 9, 28, 18, 0, 0)
        )
    

    def test_utc_datetime(self):
        self.assertEqual(
            timestamp_to_datetime(1222624800, pytz.UTC, "H"),
            datetime(2008, 9, 28, 18, 0, 0, tzinfo=pytz.UTC)
        )
    

    def test_tz_datetime(self):
        self.assertEqual(
            timestamp_to_datetime(1222624800, pytz.timezone("Europe/London"), "H"),
            pytz.timezone("Europe/London").localize(datetime(2008, 9, 28, 19, 0, 0))
        )
    

    def test_date(self):
        self.assertEqual(
            timestamp_to_datetime(1222624800, None, "D"),
            date(2008, 9, 28)
        )
