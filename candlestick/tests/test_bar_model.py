from datetime import datetime
import pytz
from django.test import TestCase
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer
from unittest.mock import patch, PropertyMock
from candlestick.models import Bar, Instrument

class BarCreationTests(TestCase):

    def test_can_make_bar(self):
        instrument = mixer.blend(Instrument)
        bar = Bar.objects.create(
            timestamp=1000, open=1, low=0, high=3, close=2, volume=10,
            resolution="30s", instrument=instrument
        )
        self.assertEqual(str(bar), "1000: 2")
    

    def test_bar_resolution_validation(self):
        invalids = ["X", "3x", "100H"]
        instrument = mixer.blend(Instrument)
        for res in invalids:
            with self.assertRaises(ValidationError):
                Bar.objects.create(
                    timestamp=1000, open=1, low=0, high=3, close=2, volume=10,
                    resolution=res, instrument=instrument
                )



class BarOrdering(TestCase):

    def test_bars_ordered_by_name(self):
        b1 = mixer.blend(Bar, timestamp=100, resolution="H")
        b2 = mixer.blend(Bar, timestamp=300, resolution="H")
        b3 = mixer.blend(Bar, timestamp=200, resolution="H")
        self.assertEqual(list(Bar.objects.all()), [b1, b3, b2])



class EndTimestampTests(TestCase):

    def test_simple_end_timestamps(self):
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="s").end_timestamp, 101)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="1s").end_timestamp, 101)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="30s").end_timestamp, 130)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="m").end_timestamp, 160)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="1m").end_timestamp, 160)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="2m").end_timestamp, 220)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="H").end_timestamp, 3700)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="1H").end_timestamp, 3700)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="6H").end_timestamp, 21700)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="D").end_timestamp, 86500)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="2D").end_timestamp, 172900)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="W").end_timestamp, 604900)
        self.assertEqual(mixer.blend(Bar, timestamp=100, resolution="4W").end_timestamp, 2419300)
    

    def test_month_timestamps(self):
        self.assertEqual(mixer.blend(Bar, timestamp=500, resolution="M").end_timestamp, 2678900)
        self.assertEqual(mixer.blend(Bar, timestamp=12000, resolution="3M").end_timestamp, 7788000)
    

    def test_year_timestamps(self):
        self.assertEqual(mixer.blend(Bar, timestamp=50000, resolution="Y").end_timestamp, 31586000)
        self.assertEqual(mixer.blend(Bar, timestamp=50000, resolution="5Y").end_timestamp, 157816400)



class StartDatetimeTests(TestCase):

    def test_naive_start_datetime(self):
        instrument = mixer.blend(Instrument)
        bar = mixer.blend(Bar, timestamp=1222624800, resolution="H", instrument=instrument)
        self.assertEqual(bar.datetime, datetime(2008, 9, 28, 18, 0, 0))
    

    def test_utc_start_datetime(self):
        instrument = mixer.blend(Instrument, timezone="UTC")
        bar = mixer.blend(Bar, timestamp=1222624800, resolution="H", instrument=instrument)
        self.assertEqual(bar.datetime, datetime(2008, 9, 28, 18, 0, 0, tzinfo=pytz.UTC))
    

    def test_tz_start_datetime(self):
        instrument = mixer.blend(Instrument, timezone="Europe/London")
        bar = mixer.blend(Bar, timestamp=1222624800, resolution="H", instrument=instrument)
        self.assertEqual(bar.datetime, pytz.timezone("Europe/London").localize(datetime(2008, 9, 28, 19, 0, 0)))



class EndDatetimeTests(TestCase):

    def setUp(self):
        self.patch1 = patch("candlestick.models.Bar.end_timestamp", new_callable=PropertyMock)
        mock_end = self.patch1.start()
        mock_end.return_value = 1222624800
    

    def tearDown(self):
        self.patch1.stop()


    def test_naive_end_datetime(self):
        instrument = mixer.blend(Instrument)
        bar = mixer.blend(Bar, timestamp=0, resolution="H", instrument=instrument)
        self.assertEqual(bar.end_datetime, datetime(2008, 9, 28, 18, 0, 0))
        
    

    def test_utc_end_datetime(self):
        instrument = mixer.blend(Instrument, timezone="UTC")
        bar = mixer.blend(Bar, timestamp=0, resolution="H", instrument=instrument)
        self.assertEqual(bar.end_datetime, datetime(2008, 9, 28, 18, 0, 0, tzinfo=pytz.UTC))
    

    def test_tz_end_datetime(self):
        instrument = mixer.blend(Instrument, timezone="Europe/London")
        bar = mixer.blend(Bar, timestamp=0, resolution="H", instrument=instrument)
        self.assertEqual(bar.end_datetime, pytz.timezone("Europe/London").localize(datetime(2008, 9, 28, 19, 0, 0)))