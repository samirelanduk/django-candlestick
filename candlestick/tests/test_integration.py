from datetime import date
from django.test import TestCase
import pytz
from candlestick.models import *

class TestModels(TestCase):

    fixtures = ["instruments.json", "bars.json"]

    def test_instruments(self):
        self.assertEqual(Instrument.objects.count(), 3)
        self.assertEqual(Instrument.objects.filter(exchange="NASDAQ").count(), 2)
        apple = Instrument.objects.get(symbol="AAPL")
        self.assertEqual(float(apple.latest_price), 309.39001)
    

    def test_bars(self):
        apple = Instrument.objects.get(symbol="AAPL")

        days = apple.bars.filter(resolution="D")
        self.assertEqual(days.count(), 21)
        self.assertEqual(float(days.first().open), 73.192)
        self.assertEqual(float(days.last().close), 76.47063)
        self.assertEqual(days.last().datetime, date(2020, 1, 31))

        hours = apple.bars.filter(resolution="H")
        self.assertEqual(hours.count(), 147)
        self.assertEqual(float(hours.first().open), 296.23999)
        self.assertEqual(float(hours.last().close), 309.39001)
        self.assertEqual(hours.last().datetime, pytz.timezone("America/New_York").localize(datetime(2020, 1, 31, 15, 30)))
