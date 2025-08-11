import re
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta


def format_timestamp(iso_str: str) -> str:
    timestamp = parser.isoparse(iso_str)
    now = datetime.utcnow()
    delta = relativedelta(now, timestamp)

    if delta.years or delta.months or delta.days > 1:
        return timestamp.strftime("%b %d, %Y %H:%M")
    elif delta.days == 1:
        return "Yesterday at " + timestamp.strftime("%H:%M")
    elif delta.hours:
        return f"{delta.hours}h ago"
    elif delta.minutes:
        return f"{delta.minutes}m ago"
    else:
        return "Just now"


def print_highlighted(text: str, title: str = "Output"):
    print(f"\n\033[92m{'=' * 40}")
    print(title)
    print('-' * 40)
    print(text)
    print("=" * 40 + "\033[0m\n")
