from datetime import datetime
from re import search, sub
from time import gmtime, strftime


def parse_timestamp(timestamp):

    # FORMAT '2021-05-01 10:30:00+03:00'
    if search(r'^\d\d\d\d-', timestamp) is not None:
        f_s = search(r'^(?P<year>\d\d\d\d)-(?P<month>\d+)-(?P<day>\d+)', timestamp)
        timestamp = sub(f_s[0], f'{f_s["day"]}-{f_s["month"]}-{f_s["year"]}', timestamp)

    # TIMEZONE
    tz_regex = r'([+\-]\d\d?):?(\d\d?)?$'
    tz = search(tz_regex, timestamp)
    if tz is None:
        tz = strftime("%z", gmtime())
        timestamp += tz
    else:
        tz = tz[0]
        tz_s = search(tz_regex, tz)
        h, m = tz_s[1], tz_s[2]
        if not h:
            h = '0'
        if not m:
            m = '0'
        h = h[0] + h[1:].zfill(2)
        m = m.zfill(2)
        tz = h + m
        timestamp = sub(f'\\{tz_s[0]}', tz, timestamp)

    # SECONDS
    if search(r'\d\d:\d\d:\d\d', timestamp) is None:
        timestamp = timestamp[:-5] + ':00' + timestamp[-5:]

    # MICROsECONDS
    ms_s = search(r'\d\d:\d\d:\d\d(\.\d+)', timestamp)
    if ms_s is not None:
        microseconds = ms_s[1]
        timestamp = sub(f'\\{microseconds}', '', timestamp)

    ts = datetime.strptime(timestamp, '%d-%m-%Y %H:%M:%S%z')
    return ts


if __name__ == '__main__':
    tts = (
        # '01-01-2020 15:42',
        # '01-01-2020 15:42+3',
        # '01-01-2020 15:42+3:30',
        # '01-01-2020 15:42+3:0',
        # '01-01-2020 15:42-3',
        # '01-01-2020 15:42-3:30',
        # '01-01-2020 15:42-3:0',

        # '01-01-2020 15:42:55',
        # '01-01-2020 15:42:55+3',
        # '01-01-2020 15:42:55+3:30',
        # '01-01-2020 15:42:55+3:0',
        # '01-01-2020 15:42:55-3',
        # '01-01-2020 15:42:55-3:30',
        # '01-01-2020 15:42:55-3:0',

        # '01-01-2020 15:42:55.038726',
        # '01-01-2020 15:42:55.038726+3',
        # '01-01-2020 15:42:55.038726+3:30',
        # '01-01-2020 15:42:55.038726+3:0',
        # '01-01-2020 15:42:55.038726-3',
        # '01-01-2020 15:42:55.038726-3:30',
        # '01-01-2020 15:42:55.038726-3:0',

        # '2020-01-01 15:42:55',
        # '2020-12-30 15:42:55+3',
    )
    for tt in tts:
        print(parse_timestamp(tt))
