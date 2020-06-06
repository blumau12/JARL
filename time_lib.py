from pandas import Timestamp
from tzlocal import get_localzone

from exceptions import assert_person


def parse_timestamp(timestamp):
    ts = Timestamp(timestamp)
    if ts.tz is None:
        ts = Timestamp(timestamp, tz=get_localzone())
    assert_person(ts.tz is not None,
                  "every timestamp should have timezone information")
    return ts
