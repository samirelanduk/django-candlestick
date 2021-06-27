import yfinance as yf
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
    save_bars(history, instrument, resolution)


def update(instrument, resolution):
    last = instrument.bars.filter(resolution=resolution).last()
    if not last: fetch(instrument, resolution)
    ticker = yf.Ticker(instrument.symbol)
    start = get_start_date(last.timestamp)
    interval, _ = get_yahoo_params(resolution)
    history = ticker.history(start=str(datetime.utcfromtimestamp(start).date()), interval=interval)
    instrument.bars.filter(
        resolution=resolution, timestamp__gte=start
    ).delete()
    save_bars(history, instrument, resolution)



def get_yahoo_params(resolution):
    """Works out which params are needed to request all data for a given
    resolution."""

    resolution = "".join([char for char in resolution if not char.isdigit()])
    intervals = {"M": "1mo", "W": "1wk", "D": "1d", "H": "60m", "m": "1m"}
    periods = {"M": "max", "W": "max", "D": "max", "H": "2y", "m": "7d"}
    if resolution not in intervals:
        raise ValueError(f"Resolution {resolution} is not valid - must be {', '.join(intervals.keys())}")
    return (intervals[resolution], periods[resolution])


def save_bars(df, instrument, resolution):
    bars = [Bar(
        instrument=instrument, resolution=resolution,
        open=round(bar.Open, 3), close=round(bar.Close, 3),
        high=round(bar.High, 3), low=round(bar.Low, 3),
        volume=bar.Volume, timestamp=datetime.timestamp(bar.name)
    ) for bar in df.iloc()]
    Bar.objects.bulk_create(bars)


def get_start_date(timestamp):
    start = timestamp - (timestamp % 86400)
    start -= 86400 * 1
    return start
        
