#! /usr/bin/python3

import os
import parser
from manifest import Report

date = parser.check_date()
manifest_filename = f"{date}.json"
report = Report(os.getcwd(), manifest_filename)
report.check_manifest()
log_txt = report.log(color=True)
print(log_txt)
