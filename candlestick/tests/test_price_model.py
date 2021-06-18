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
