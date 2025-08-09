from datetime import datetime
from zoneinfo import ZoneInfo


def generate_trace_id(tz_name: str = "UTC") -> str:
    tz = ZoneInfo(tz_name)
    now = datetime.now(ZoneInfo("UTC")).astimezone(tz)
    return now.strftime("%Y%m%dT%H%M%S%z")
