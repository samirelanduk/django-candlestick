from django.core.management.base import BaseCommand, CommandError
from candlestick.models import Instrument

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
        bars = instrument.fetch(options["resolution"])
        self.stdout.write(self.style.SUCCESS(
            f"{len(bars)} bar{'' if len(bars) == 1 else 's'} saved for {symbol}"
        ))