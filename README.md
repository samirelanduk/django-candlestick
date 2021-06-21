# django-candlestick

![](https://github.com/samirelanduk/django-candlestick/actions/workflows/main.yml/badge.svg)
![](https://img.shields.io/github/last-commit/samirelanduk/django-candlestick/master.svg)
[![](https://img.shields.io/pypi/pyversions/django-candlestick.svg?color=3776AB&logo=python&logoColor=white)](https://www.python.org/)
[![](https://img.shields.io/pypi/djversions/django-candlestick?color=0C4B33&logo=django&logoColor=white&label=django)](https://www.djangoproject.com/)
[![](https://img.shields.io/pypi/l/django-candlestick.svg?color=blue)](https://github.com/samirelanduk/django-candlestick/blob/master/LICENSE)

django-candlestick is a django library for storing price data for stocks, assets,
currencies, and other tradeable instruments.

## Setup

Install:

```bash
$ pip install django-candlestick
```

Add to installed apps:

```python
INSTALLED_APPS = [
    ...
    "candlestick"
    ...
]
```

Migrate:

```bash
$ python manage.py migrate
```

You now have a database of tradeable instruments and their prices.

## Use

```python
from django_candlestick.models import Instrument, Bar

apple = Instrument.objects.create(
    symbol="AAPL", name="Apple, Inc.", currency="USD", timezone="US/Eastern"
)
bar = Bar.objects.create(
    open="320.13", low="319.88", high="321.4", close="320.17", volume=3115337,
    timestamp=1579887000, resolution="H", instrument=apple
)
print(bar.datetime) # 2020-01-24 12:30:00-05:00
```