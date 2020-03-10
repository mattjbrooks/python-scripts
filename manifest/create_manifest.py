#! /usr/bin/python3

import datetime
import os
from manifest import Manifest

date = datetime.datetime.now().strftime('%Y-%m-%d')
manifest_filename = f"{date}.json"
manifest = Manifest(os.getcwd(), manifest_filename)
manifest.create_manifest_files()
