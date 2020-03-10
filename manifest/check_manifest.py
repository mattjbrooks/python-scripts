#! /usr/bin/python3

import os
import manifest
import parser

date = parser.check_date()
manifest_filename = f"{date}.json"
manifest = manifest.Manifest(os.getcwd(), manifest_filename)
manifest.check_manifest()
