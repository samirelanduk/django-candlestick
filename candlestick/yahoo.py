import yfinance as yf
import numpy as np
from datetime import datetime
from candlestick.models import Bar

def fetch(instrument, resolution):
    """Gets bars from Yahoo for a specific instrument and resolution. Existing
    bars will be overwritten if they fall within the range."""

    ticker = yf.Ticker(instrument.symbol)
    interval, period = get_yahoo_params(resolution)
    history = ticker.history(period=period, interval=interval)
    start = datetime.timestamp(history.iloc[0].name)
    end = datetime.timestamp(history.iloc[-1].name)
    instrument.bars.filter(
        resolution=resolution, timestamp__gte=start, timestamp__lte=end
    ).delete()
    return save_bars(history, instrument, resolution)


def update(instrument, resolution):
    """Gets new bars for an instrument. The most recent bar for the resolution
    will be deleted and refetched, along with any more recent than it."""

    last = instrument.bars.filter(resolution=resolution).last()
    if not last: return fetch(instrument, resolution)
    start = get_start_date(last.timestamp, resolution)
    interval, _ = get_yahoo_params(resolution)
    ticker = yf.Ticker(instrument.symbol)
    history = ticker.history(start=str(datetime.utcfromtimestamp(start).date()), interval=interval)
    instrument.bars.filter(
        resolution=resolution, timestamp__gte=start
    ).delete()
    return save_bars(history, instrument, resolution)


def save_bars(df, instrument, resolution):
    """Saves a Pandas dataframe of prices to database."""

    bars = [Bar(
        instrument=instrument, resolution=resolution,
        open=round(bar.Open, 3), close=round(bar.Close, 3),
        high=round(bar.High, 3), low=round(bar.Low, 3),
        volume=int(bar.Volume), timestamp=datetime.timestamp(bar.name)
    ) for bar in df.replace({np.nan: 0}).iloc()]
    return Bar.objects.bulk_create(bars)


def get_yahoo_params(resolution):
    """Works out which params are needed to request all data for a given
    resolution."""

    if resolution[0] == "1" and len(resolution) > 1 and resolution[1].isalpha():
        resolution = resolution[1:]
    lookup = {
        "m": ("1m", "7d"), "2m": ("2m", "7d"), "5m": ("5m", "60d"),
        "15m": ("15m", "60d"), "30m": ("30m", "60d"), "H": ("60m", "2y"),
        "D": ("1d", "100y"), "5D": ("5d", "100y"), "W": ("1wk", "100y"),
        "M": ("1mo", "100y"), "3M": ("3mo", "100y")
    }
    if resolution not in lookup:
        raise ValueError(f"Resolution {resolution} is not valid - must be {', '.join(lookup.keys())}")
    return lookup[resolution]


def get_start_date(timestamp, resolution):
    """Works out which date timestamp to ask for to ensure a particular
    timestamp is refetched.

    For intraday resolutions, the timestamp is rolled back to the previous
    midnight, and then back another 24 hours.

    For D resolution, the timestamp is returned unaltered. For higher D
    resolutions, the timestamp is rolled back by the appropriate number of
    days. For W and M resolutions, the same logic is used but for 7 and 35 days
    respectively."""

    num = int("".join(char for char in resolution if char.isdigit()) or "1")
    if any(char in resolution for char in "mH"):
        return timestamp - (timestamp % 86400) - 86400
    elif resolution in ["D", "1D"]:
        return timestamp
    elif "D" in resolution:
        return timestamp - (num * 86400)
    elif "W" in resolution:
        return timestamp - (num * 86400 * 7)
    else:
        return timestamp - (num * 86400 * 35)