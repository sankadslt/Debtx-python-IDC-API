from datetime import datetime
from zoneinfo import ZoneInfo

def get_sri_lanka_time():
    utc_time = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
    sl_time = utc_time.astimezone(ZoneInfo("Asia/Colombo"))
    return sl_time
