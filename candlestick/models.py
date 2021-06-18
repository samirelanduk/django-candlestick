from django.db import models

class Instrument(models.Model):
    """A tradeable entity."""

    class Meta:
        ordering = ["symbol"]

    symbol = models.CharField(max_length=10)
    exchange = models.CharField(max_length=20, blank=True, null=True)
    currency = models.CharField(max_length=20)
    category = models.CharField(max_length=100)
