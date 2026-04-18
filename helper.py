from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta


def parse_expiration(expiration_str):
    """Parse a TradingView expiration string to a timezone-aware datetime."""
    if not expiration_str:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(expiration_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc)


def format_expiration(dt):
    """Format a datetime to the string format TradingView expects."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def get_access_extension(current_expiration_str, extension_type, extension_length):
    """
    Calculate a new expiration date by extending from the current expiration
    (or now, whichever is later).

    extension_type:
        "D" = days
        "W" = weeks
        "M" = months
        "Y" = years
        "L" = lifetime (no expiration - handled in caller)

    Returns a formatted expiration string.
    """
    now = datetime.now(timezone.utc)
    current = parse_expiration(current_expiration_str)

    # If the current expiration is in the past, extend from now
    base = max(now, current)

    extension_type = extension_type.upper()

    if extension_type == "D":
        new_expiry = base + timedelta(days=extension_length)
    elif extension_type == "W":
        new_expiry = base + timedelta(weeks=extension_length)
    elif extension_type == "M":
        new_expiry = base + relativedelta(months=extension_length)
    elif extension_type == "Y":
        new_expiry = base + relativedelta(years=extension_length)
    else:
        # Default to 30 days if unknown type
        new_expiry = base + timedelta(days=30)

    return format_expiration(new_expiry)
