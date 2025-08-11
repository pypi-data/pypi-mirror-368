import re
from datetime import datetime
from zoneinfo import ZoneInfo

_TRACE_ID_RE = re.compile(r"\d{8}T\d{6}[+-]\d{4}$")


def generate_trace_id(tz_name: str = "UTC") -> str:
    tz = ZoneInfo(tz_name)
    now = datetime.now(ZoneInfo("UTC")).astimezone(tz)
    return now.strftime("%Y%m%dT%H%M%S%z")


def is_valid_trace_id(value: str) -> bool:
    return bool(_TRACE_ID_RE.fullmatch(value))
