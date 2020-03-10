#! /usr/bin/python3

import datetime
import os
import manifest

date = datetime.datetime.now().strftime('%Y-%m-%d')
manifest_filename = f"{date}.json"
manifest = manifest.Manifest(os.getcwd(), manifest_filename)
manifest.create_manifest()
