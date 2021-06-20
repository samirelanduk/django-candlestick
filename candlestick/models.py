from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from timezone_field import TimeZoneField
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import pre_save
from candlestick.utils import timestamp_to_datetime

class Instrument(models.Model):
    """A tradeable entity."""

    class Meta:
        ordering = ["symbol"]

    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=100, blank=True, null=True)
    exchange = models.CharField(max_length=20, blank=True, null=True)
    currency = models.CharField(max_length=20)
    timezone = TimeZoneField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.symbol
    
    @receiver(pre_save)
    def pre_save_handler(sender, instance, *args, **kwargs):
        instance.full_clean()


    @property
    def latest_price(self):
        """The close price of the most recent bar."""

        bar = self.bars.last()
        if bar: return bar.close



class Bar(models.Model):
    """The price of an instrument over some period of time.
    
    If the resolution is D or above, the timestamp must be a UNIX midnight
    timestamp."""

    class Meta:
        ordering = ["timestamp"]

    timestamp = models.IntegerField()
    resolution = models.CharField(validators=[RegexValidator("^\d{0,2}[smHDWMY]$")], max_length=3)
    open = models.DecimalField(max_digits=15, decimal_places=6)
    low = models.DecimalField(max_digits=15, decimal_places=6)
    high = models.DecimalField(max_digits=15, decimal_places=6)
    close = models.DecimalField(max_digits=15, decimal_places=6)
    volume = models.IntegerField()
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="bars")

    def __str__(self):
        return f"{self.timestamp} ({self.close})"

    @receiver(pre_save)
    def pre_save_handler(sender, instance, *args, **kwargs):
        instance.full_clean()
    

    def clean(self): 
        if self.resolution[-1] in "DWMY" and self.timestamp % 86400:
            raise ValidationError(
                f"Timestamp {self.timestamp} is invalid for resolution {self.resolution}"
            )


    @property
    def end_timestamp(self):
        """What is the timestamp at the end of the period represented by this
        bar?"""

        count, res = int(self.resolution[:-1] or 1), self.resolution[-1]
        if res in "MY":
            if res == "Y": count *= 12
            dt = datetime.utcfromtimestamp(self.timestamp)
            dt += relativedelta(months=count)
            return calendar.timegm(dt.utctimetuple())
        secs = count * {"s": 1, "m": 60, "H": 3600, "D": 86400, "W": 604800}[res]
        return self.timestamp + secs
    

    @property
    def datetime(self):
        """Returns the timestamp as a Python datetime - naive if the instrument
        has no timezone, aware if it does."""

        return timestamp_to_datetime(
            self.timestamp, self.instrument.timezone, self.resolution
        )
    

    @property
    def end_datetime(self):
        """Returns the end timestamp as a Python datetime - naive if the
        instrument has no timezone, aware if it does."""

        return timestamp_to_datetime(
            self.end_timestamp, self.instrument.timezone, self.resolution
        )
