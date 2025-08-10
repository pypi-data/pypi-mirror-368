from datetime import datetime
import pytz
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

__version__ = "1.0.0"

TIMEZONE_MAP = {
    'PST': 'US/Pacific',
    'BST': 'Europe/London', 
    'WAT': 'Africa/Lagos',
    'CET': 'Europe/Berlin',
    'EST': 'US/Eastern'
}

def get_time_in_timezone(tz_code):
    if tz_code not in TIMEZONE_MAP:
        raise ValueError(f"Unsupported timezone: {tz_code}")
    
    tz_name = TIMEZONE_MAP[tz_code]
    tz = pytz.timezone(tz_name)
    current_time = datetime.now(tz)
    
    logger.info(f"Retrieved time for {tz_code}: {current_time}")
    return current_time

def get_all_times():
    times = {}
    for tz_code in TIMEZONE_MAP.keys():
        times[tz_code] = get_time_in_timezone(tz_code)
    return times