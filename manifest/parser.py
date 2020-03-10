import datetime
import re
import sys


def check_date():
    if len(sys.argv) != 2:
        error_msg()
    dateRegex = re.compile(r'[1-2]\d\d\d-[0-1]\d-[0-3]\d')
    matchObject = dateRegex.search(sys.argv[1])
    if matchObject:
        date = matchObject.group()
    else:
        error_msg()
    if date != sys.argv[1]:
        error_msg()
    year, month, day = date.split('-')
    try:
        datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        error_msg()
    return date


def error_msg():
    print("Usage: check_manifests YYYY-MM-DD")
    sys.exit()
