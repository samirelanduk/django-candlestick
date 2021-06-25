import pandas as pd
from django.test import TestCase
from datetime import timezone
from unittest.mock import patch, Mock
from mixer.backend.django import mixer
from candlestick.models import Instrument, Bar
from candlestick.yahoo import fetch, get_yahoo_params

class FetchTests(TestCase):

    def setUp(self):
        self.instrument = mixer.blend(Instrument, symbol="AAPL")
        self.patch1 = patch("yfinance.Ticker")
        self.patch2 = patch("candlestick.yahoo.get_yahoo_params")
        self.mock_ticker = self.patch1.start()
        self.mock_params = self.patch2.start()
        self.mock_params.return_value = ["D", "max"]
        self.Ticker = Mock()
        df = pd.DataFrame(
            data = {
                "Open": [10, 20, 30], 
                "Close": [12, 22, 32], 
                "High": [14, 24, 34],
                "Low": [8, 18, 28],
                "Volume": [100, 200, 300]
            },
            columns=["Open", "Close", "High", "Low", "Volume"],
            index=[
                pd.Timestamp(946684800, unit="s", tzinfo=timezone.utc),
                pd.Timestamp(946771200, unit="s", tzinfo=timezone.utc),
                pd.Timestamp(946857600, unit="s", tzinfo=timezone.utc),
            ]
        )
        df.index.name = "Date"
        self.Ticker.history.return_value = df
        self.mock_ticker.return_value = self.Ticker
    

    def tearDown(self):
        self.patch1.stop()


    def test_can_fetch_bars(self):
        with self.assertNumQueries(2):
            fetch(self.instrument, "D")
        self.mock_ticker.assert_called_with("AAPL")
        self.mock_params.assert_called_with("D")
        self.Ticker.history.assert_called_with(period="max", interval="D")
        self.assertEqual(self.instrument.bars.count(), 3)
        bar = self.instrument.bars.first()
        self.assertEqual(bar.open, 10)
        self.assertEqual(bar.volume, 100)
        self.assertEqual(bar.timestamp, 946684800)
        self.assertEqual(bar.resolution, "D")
        self.assertEqual(bar.instrument, self.instrument)
        bar = self.instrument.bars.last()
        self.assertEqual(bar.open, 30)
    

    def test_can_fetch_bars_and_replace(self):
        mixer.blend(Bar, timestamp=946684800, resolution="D", instrument=self.instrument)
        mixer.blend(Bar, timestamp=946857600, resolution="W", instrument=self.instrument)
        with self.assertNumQueries(2):
            fetch(self.instrument, "D")
        self.mock_ticker.assert_called_with("AAPL")
        self.mock_params.assert_called_with("D")
        self.Ticker.history.assert_called_with(period="max", interval="D")
        self.assertEqual(self.instrument.bars.filter(resolution="D").count(), 3)
        bar = self.instrument.bars.first()
        self.assertEqual(bar.open, 10)
        self.assertEqual(bar.volume, 100)
        self.assertEqual(bar.timestamp, 946684800)
        self.assertEqual(bar.resolution, "D")
        self.assertEqual(bar.instrument, self.instrument)
        bar = self.instrument.bars.filter(resolution="D").last()
        self.assertEqual(bar.open, 30)



class YahooParamsFromResolutionTests(TestCase):

    def test_can_get_params(self):
        self.assertEqual(get_yahoo_params("M"), ("1mo", "max"))
        self.assertEqual(get_yahoo_params("W"), ("1wk", "max"))
        self.assertEqual(get_yahoo_params("D"), ("1d", "max"))
        self.assertEqual(get_yahoo_params("H"), ("60m", "2y"))
        self.assertEqual(get_yahoo_params("m"), ("1m", "7d"))
    

    def test_can_get_strip_numbers(self):
        self.assertEqual(get_yahoo_params("3M"), ("1mo", "max"))
        self.assertEqual(get_yahoo_params("2W"), ("1wk", "max"))
        self.assertEqual(get_yahoo_params("5D"), ("1d", "max"))
        self.assertEqual(get_yahoo_params("6H"), ("60m", "2y"))
        self.assertEqual(get_yahoo_params("30m"), ("1m", "7d"))
    

    def test_can_handle_invalid_resolution(self):
        with self.assertRaises(ValueError) as e:
            get_yahoo_params("X")
        self.assertIn("M, W, D, H, m", str(e.exception))
