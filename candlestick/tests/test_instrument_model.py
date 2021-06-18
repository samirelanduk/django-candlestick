from django.test import TestCase
from mixer.backend.django import mixer
from candlestick.models import Instrument

class InstrumentCreationTests(TestCase):

    def test_can_make_instrument(self):
        instrument = Instrument.objects.create(symbol="AAPL", currency="USD")
        self.assertEqual(str(instrument), "AAPL")
        self.assertFalse(instrument.prices.all())
        self.assertEqual(instrument.category, None)
        self.assertEqual(instrument.exchange, None)
    

    def test_can_make_full_instrument(self):
        Instrument.objects.create(
            symbol="AAPL", currency="USD", exchange="NASDAQ", category="US"
        )



class InstrumentOrdering(TestCase):

    def test_instruments_ordered_by_name(self):
        i1 = mixer.blend(Instrument, symbol="A")
        i2 = mixer.blend(Instrument, symbol="C")
        i3 = mixer.blend(Instrument, symbol="B")
        self.assertEqual(list(Instrument.objects.all()), [i1, i3, i2])
