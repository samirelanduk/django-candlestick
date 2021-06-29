from django.core.management.base import BaseCommand, CommandError
from candlestick.models import Instrument
from time import time

class Command(BaseCommand):
    help = "Fetches all available data for an instrument"


    def add_arguments(self, parser):
        parser.add_argument("symbol", type=str)
        parser.add_argument("resolution", type=str)


    def handle(self, *args, **options):
        symbol = options["symbol"]
        try:
            instrument = Instrument.objects.get(symbol=symbol)
        except Instrument.DoesNotExist:
            raise CommandError('Instrument "%s" does not exist' % symbol)
        try:
            start = time()
            bars = instrument.fetch(options["resolution"])
            duration = round(time() - start, 2)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"{symbol}: {str(e)}"))
        self.stdout.write(self.style.SUCCESS(
            f"{len(bars)} {options['resolution']} bar{'' if len(bars) == 1 else 's'} saved for {symbol} ({duration}s)"
        ))