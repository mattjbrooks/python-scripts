#! /usr/bin/python3

import os
import parser
from manifest import Report

date = parser.check_date()
report = Report(manifest_filename=f"{date}.json")
print(report.log(color=True))
