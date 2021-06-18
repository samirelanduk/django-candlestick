from django.db import models
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import pre_save

class Instrument(models.Model):
    """A tradeable entity."""

    class Meta:
        ordering = ["symbol"]

    symbol = models.CharField(max_length=10)
    exchange = models.CharField(max_length=20, blank=True, null=True)
    currency = models.CharField(max_length=20)
    category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.symbol
    
    @receiver(pre_save)
    def pre_save_handler(sender, instance, *args, **kwargs):
        instance.full_clean()



class Price(models.Model):
    """The price of an instrument over some period of time."""

    class Meta:
        ordering = ["timestamp"]

    timestamp = models.IntegerField()
    resolution = models.CharField(validators=[RegexValidator("^\d{0,2}[smHDWMY]$")], max_length=3)
    open = models.DecimalField(max_digits=9, decimal_places=5)
    low = models.DecimalField(max_digits=9, decimal_places=5)
    high = models.DecimalField(max_digits=9, decimal_places=5)
    close = models.DecimalField(max_digits=9, decimal_places=5)
    volume = models.IntegerField()
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="prices")

    def __str__(self):
        return f"{self.timestamp}: {self.close}"

    @receiver(pre_save)
    def pre_save_handler(sender, instance, *args, **kwargs):
        instance.full_clean()
