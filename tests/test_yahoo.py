import pandas as pd
import numpy as np
from django.test import TestCase
from datetime import timezone
from unittest.mock import patch, Mock
from mixer.backend.django import mixer
from candlestick.models import Instrument, Bar
from candlestick.yahoo import fetch, update, get_start_date, get_yahoo_params, save_bars

class FetchTests(TestCase):

    def setUp(self):
        self.instrument = mixer.blend(Instrument, symbol="AAPL")
        self.patch1 = patch("yfinance.Ticker")
        self.patch2 = patch("candlestick.yahoo.get_yahoo_params")
        self.patch3 = patch("candlestick.yahoo.save_bars")
        self.mock_ticker = self.patch1.start()
        self.mock_params = self.patch2.start()
        self.mock_params.return_value = ["D", "max"]
        self.mock_save = self.patch3.start()
        self.Ticker = Mock()
        df = pd.DataFrame(
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
        self.patch2.stop()
        self.patch3.stop()


    def test_can_fetch_bars(self):
        with self.assertNumQueries(1):
            bars = fetch(self.instrument, "D")
        self.mock_ticker.assert_called_with("AAPL")
        self.mock_params.assert_called_with("D")
        self.Ticker.history.assert_called_with(period="max", interval="D")
        self.mock_save.assert_called_with(self.Ticker.history.return_value, self.instrument, "D")
        self.assertEqual(bars, self.mock_save.return_value)


    def test_can_fetch_bars_and_replace(self):
        mixer.blend(Bar, timestamp=86400, resolution="D", instrument=self.instrument)
        mixer.blend(Bar, timestamp=946684800, resolution="D", instrument=self.instrument)
        mixer.blend(Bar, timestamp=946857600, resolution="W", instrument=self.instrument)
        with self.assertNumQueries(1):
            bars = fetch(self.instrument, "D")
        self.mock_ticker.assert_called_with("AAPL")
        self.mock_params.assert_called_with("D")
        self.Ticker.history.assert_called_with(period="max", interval="D")
        self.mock_save.assert_called_with(self.Ticker.history.return_value, self.instrument, "D")
        self.assertEqual(self.instrument.bars.filter(resolution="D").count(), 1)
        self.assertEqual(bars, self.mock_save.return_value)



class UpdateTests(TestCase):

    def setUp(self):
        self.instrument = mixer.blend(Instrument, symbol="AAPL")
        self.patch1 = patch("candlestick.yahoo.get_start_date")
        self.patch2 = patch("candlestick.yahoo.get_yahoo_params")
        self.patch3 = patch("yfinance.Ticker")
        self.patch4 = patch("candlestick.yahoo.save_bars")
        self.mock_start = self.patch1.start()
        self.mock_start.return_value = 86400
        self.mock_params = self.patch2.start()
        self.mock_params.return_value = ["1d", "max"]
        self.mock_ticker = self.patch3.start()
        self.Ticker = Mock()
        self.mock_ticker.return_value = self.Ticker
        self.mock_save = self.patch4.start()
    

    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    @patch("candlestick.yahoo.fetch")
    def test_can_default_to_fetch(self, mock_fetch):
        update(self.instrument, "D")
        mock_fetch.assert_called_with(self.instrument, "D")
    

    def test_updating(self):
        mixer.blend(Bar, timestamp=946684800, resolution="D", instrument=self.instrument)
        bars = update(self.instrument, "D")
        self.mock_start.assert_called_with(946684800, "D")
        self.mock_ticker.assert_called_with("AAPL")
        self.Ticker.history.assert_called_with(start="1970-01-02", interval="1d")
        self.mock_save.assert_called_with(self.Ticker.history.return_value, self.instrument, "D")
        self.assertEqual(self.instrument.bars.filter(resolution="D").count(), 0)
        self.assertEqual(bars, self.mock_save.return_value)



class BarSavingTests(TestCase):

    def test_can_save_bars(self):
        instrument = mixer.blend(Instrument, symbol="AAPL")
        df = pd.DataFrame(
            data = {
                "Open": [10, 20, 30],  "Close": [12, 22, 32], 
                "High": [14, 24, 34], "Low": [8, 18, 28],
                "Volume": [100, 200, np.nan]
            },
            columns=["Open", "Close", "High", "Low", "Volume"],
            index=[
                pd.Timestamp(946684800, unit="s", tzinfo=timezone.utc),
                pd.Timestamp(946771200, unit="s", tzinfo=timezone.utc),
                pd.Timestamp(946857600, unit="s", tzinfo=timezone.utc),
            ]
        )
        bars = save_bars(df, instrument, "D")
        self.assertEqual(instrument.bars.count(), 3)
        self.assertEqual(len(bars), 3)
        bar = instrument.bars.first()
        self.assertEqual(bar.open, 10)
        self.assertEqual(bar.volume, 100)
        self.assertEqual(bar.timestamp, 946684800)
        self.assertEqual(bar.resolution, "D")
        self.assertEqual(bar.instrument, instrument)
        bar = instrument.bars.last()
        self.assertEqual(bar.open, 30)
        self.assertEqual(bar.volume, 0)



class YahooParamsFromResolutionTests(TestCase):

    def test_can_get_params(self):
        self.assertEqual(get_yahoo_params("m"), ("1m", "7d"))
        self.assertEqual(get_yahoo_params("2m"), ("2m", "7d"))
        self.assertEqual(get_yahoo_params("5m"), ("5m", "60d"))
        self.assertEqual(get_yahoo_params("H"), ("60m", "2y"))
        self.assertEqual(get_yahoo_params("D"), ("1d", "100y"))
        self.assertEqual(get_yahoo_params("W"), ("1wk", "100y"))
    

    def test_can_handle_invalid_resolution(self):
        with self.assertRaises(ValueError) as e:
            get_yahoo_params("X")
        self.assertIn("m, 2m, 5m, 15m, 30m, H, D, 5D, W, M, 3M", str(e.exception))



class StartDateTests(TestCase):

    def test_can_get_intra_start(self):
        self.assertEqual(get_start_date(1624518060, "m"), 1624406400)
        self.assertEqual(get_start_date(1624518300, "5m"), 1624406400)
        self.assertEqual(get_start_date(1624521060, "1H"), 1624406400)
        self.assertEqual(get_start_date(1624521060, "3H"), 1624406400)
    

    def test_can_get_D_start(self):
        self.assertEqual(get_start_date(1624406400, "D"), 1624406400)
    

    def test_can_get_5D_start(self):
        self.assertEqual(get_start_date(1624406400, "5D"), 1623974400)
    

    def test_can_get_W_start(self):
        self.assertEqual(get_start_date(1624406400, "W"), 1623801600)
    

    def test_can_get_M_start(self):
        self.assertEqual(get_start_date(1624406400, "1M"), 1621382400)
    

    def test_can_get_3M_start(self):
        self.assertEqual(get_start_date(1624406400, "3M"), 1615334400)
