from django.test import TestCase
from django.core.exceptions import ValidationError
from mixer.backend.django import mixer
from candlestick.models import Instrument, Bar

class InstrumentCreationTests(TestCase):

    def test_can_make_instrument(self):
        instrument = Instrument.objects.create(symbol="AAPL", currency="USD")
        self.assertEqual(str(instrument), "AAPL")
        self.assertFalse(instrument.bars.all())
        self.assertEqual(instrument.category, None)
        self.assertEqual(instrument.exchange, None)
        self.assertEqual(instrument.timezone, None)


    def test_can_make_full_instrument(self):
        Instrument.objects.create(
            symbol="AAPL", currency="USD", exchange="NASDAQ", category="US",
            timezone="Europe/London", name="Apple Inc."
        )
    

    def test_symbol_and_exchange_must_be_unique(self):
        Instrument.objects.create(symbol="AAPL", currency="USD", exchange="NAS1")
        Instrument.objects.create(symbol="AAPL", currency="USD", exchange="NAS2")
        with self.assertRaises(ValidationError):
            Instrument.objects.create(symbol="AAPL", currency="GBP", exchange="NAS1")



class InstrumentOrdering(TestCase):

    def test_instruments_ordered_by_name(self):
        i1 = mixer.blend(Instrument, symbol="A")
        i2 = mixer.blend(Instrument, symbol="C")
        i3 = mixer.blend(Instrument, symbol="B")
        self.assertEqual(list(Instrument.objects.all()), [i1, i3, i2])



class InstrumentLatestBar(TestCase):

    def test_can_get_no_latest_price(self):
        instrument = mixer.blend(Instrument)
        self.assertIsNone(instrument.latest_price)
    

    def test_can_get_latest_price(self):
        instrument = mixer.blend(Instrument)
        mixer.blend(Bar, timestamp=100, close=20, resolution="m", instrument=instrument)
        mixer.blend(Bar, timestamp=300, close=50, resolution="m", instrument=instrument)
        mixer.blend(Bar, timestamp=200, close=80, resolution="m", instrument=instrument)
        mixer.blend(Bar, timestamp=400, close=80, resolution="m")
        self.assertEqual(instrument.latest_price, 50)
