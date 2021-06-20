from datetime import datetime
import pytz

def timestamp_to_datetime(timestamp, timezone, resolution):
    """Converts a timestamp into a date (if a resolution above D), naive
    datetime (if no timezone is supplied) or aware datetime (if a timezone is
    supplied)."""
    
    if resolution[-1] in "DWMY":
        return datetime.utcfromtimestamp(timestamp).date()
    if not timezone:
        return datetime.utcfromtimestamp(timestamp)
    else:
        naive = datetime.utcfromtimestamp(timestamp)
        utc = pytz.utc.localize(naive, is_dst=None)
        return utc.astimezone(timezone)