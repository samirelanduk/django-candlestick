from django.test import TestCase
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer
from candlestick.models import Price, Instrument

class PriceCreationTests(TestCase):

    def test_can_make_price(self):
        instrument = mixer.blend(Instrument)
        price = Price.objects.create(
            timestamp=1000, open=1, low=0, high=3, close=2, volume=10,
            resolution="30s", instrument=instrument
        )
        self.assertEqual(str(price), "1000: 2")
    

    def test_price_resolution_validation(self):
        invalids = ["X", "3x", "100H"]
        instrument = mixer.blend(Instrument)
        for res in invalids:
            with self.assertRaises(ValidationError):
                Price.objects.create(
                    timestamp=1000, open=1, low=0, high=3, close=2, volume=10,
                    resolution=res, instrument=instrument
                )



class PriceOrdering(TestCase):

    def test_prices_ordered_by_name(self):
        p1 = mixer.blend(Price, timestamp=100, resolution="H")
        p2 = mixer.blend(Price, timestamp=300, resolution="H")
        p3 = mixer.blend(Price, timestamp=200, resolution="H")
        self.assertEqual(list(Price.objects.all()), [p1, p3, p2])



class EndTimestampTests(TestCase):

    def test_simple_end_timestamps(self):
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="s").end_timestamp, 101)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="1s").end_timestamp, 101)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="30s").end_timestamp, 130)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="m").end_timestamp, 160)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="1m").end_timestamp, 160)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="2m").end_timestamp, 220)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="H").end_timestamp, 3700)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="1H").end_timestamp, 3700)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="6H").end_timestamp, 21700)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="D").end_timestamp, 86500)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="2D").end_timestamp, 172900)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="W").end_timestamp, 604900)
        self.assertEqual(mixer.blend(Price, timestamp=100, resolution="4W").end_timestamp, 2419300)
    

    def test_month_timestamps(self):
        self.assertEqual(mixer.blend(Price, timestamp=500, resolution="M").end_timestamp, 2678900)
        self.assertEqual(mixer.blend(Price, timestamp=12000, resolution="3M").end_timestamp, 7788000)
    

    def test_year_timestamps(self):
        self.assertEqual(mixer.blend(Price, timestamp=50000, resolution="Y").end_timestamp, 31586000)
        self.assertEqual(mixer.blend(Price, timestamp=50000, resolution="5Y").end_timestamp, 157816400)