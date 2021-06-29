from django.core.management.base import BaseCommand, CommandError
from candlestick.models import Instrument
from time import time

class Command(BaseCommand):
    help = "Updates new data for an instrument"

    def add_arguments(self, parser):
        parser.add_argument("symbols", type=str)
        parser.add_argument("resolution", type=str)


    def handle(self, *args, **options):
        symbols = options["symbols"].split(",")
        if options["symbols"] == "all":
            symbols = Instrument.objects.all().values_list("symbol", flat=True)
        for symbol in symbols:
            try:
                instrument = Instrument.objects.get(symbol=symbol)
            except Instrument.DoesNotExist:
                raise CommandError('Instrument "%s" does not exist' % symbol)
            try:
                start = time()
                bars = instrument.update(options["resolution"])
                duration = round(time() - start, 2)
                self.stdout.write(self.style.SUCCESS(
                    f"{len(bars)} {options['resolution']} bar{'' if len(bars) == 1 else 's'} saved for {symbol} ({duration}s)"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{symbol}: {str(e)}"))