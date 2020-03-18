#! /usr/bin/python3

import datetime
import re
import sys
from manifest import Manifest, Report


def main():
    if len(sys.argv) not in (2, 3):
        display_help()
    if sys.argv[1] == "create" and len(sys.argv) == 2:
        create_manifest()
    elif sys.argv[1] == "check":
        check_manifest()
    else:
        display_help()


def create_manifest():
    manifest = Manifest()
    manifest.create_manifest()


def check_manifest():
    if len(sys.argv) == 3:
        date = check_date(sys.argv[2])
        report = Report(manifest_filename=f"{date}.json")
    else:
        report = Report()
    print(report.log(color=True))


def check_date(some_string):
    dateRegex = re.compile(r'[1-2]\d\d\d-[0-1]\d-[0-3]\d')
    matchObject = dateRegex.search(some_string)
    if matchObject:
        date = matchObject.group()
    else:
        display_date_format_msg()
    if some_string != date:
        display_date_format_msg()
    year, month, day = date.split('-')
    try:
        datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        display_date_format_msg()
    return date


def display_date_format_msg():
    print("Usage: manifest check YYYY-MM-DD")
    sys.exit()


def display_help():
    help_msg = """\
    Usage: manifest <command> [<args>]

    Commands:
        create          Create manifest in current directory
        check [date]    Check manifest for date of format YY-MM-DD\
    """
    print(help_msg)
    sys.exit()


if __name__ == "__main__":
    main()
