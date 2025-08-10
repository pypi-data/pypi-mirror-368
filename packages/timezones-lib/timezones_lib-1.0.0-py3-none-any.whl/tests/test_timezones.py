import pytest
from datetime import datetime
from timezones_lib import get_time_in_timezone, get_all_times, TIMEZONE_MAP

def test_supported_timezones():
    expected = {'PST', 'BST', 'WAT', 'CET', 'EST'}
    assert set(TIMEZONE_MAP.keys()) == expected

def test_get_time_in_timezone():
    for tz in TIMEZONE_MAP.keys():
        time = get_time_in_timezone(tz)
        assert isinstance(time, datetime)
        assert time.tzinfo is not None

def test_invalid_timezone():
    with pytest.raises(ValueError):
        get_time_in_timezone('INVALID')

def test_get_all_times():
    times = get_all_times()
    assert len(times) == len(TIMEZONE_MAP)
    for tz, time in times.items():
        assert tz in TIMEZONE_MAP
        assert isinstance(time, datetime)