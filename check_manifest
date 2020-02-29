#! /usr/bin/python3

import hashlib
import os
import json
import datetime
import re
import sys


class Manifest():
    def __init__(self, base_directory):
        self.base_directory = base_directory
        self.manifest_path = os.path.join(base_directory, MANIFEST_ROOT)
        self.manifest_exists = True
        self.hash_mismatches = []
        self.manifest_folders = []
        self.manifest_folders_with_manifest_file = []
        self.manifest_folders_with_no_manifest_file = []
        self.unrecorded_files = []
        self.unrecorded_folders = []
        self.recorded_but_missing_files = []
        self.recorded_but_missing_folders = []

    def __str__(self):
        return (
            f"Manifest exists: {self.manifest_exists}\n"
            f"Manifest folders: {self.manifest_folders}\n"
            f"Manifest folders with manifest file: {self.manifest_folders_with_manifest_file}\n"
            f"Manifest folders with no manifest files: {self.manifest_folders_with_no_manifest_file}\n"
            f"Unrecorded folders: {self.unrecorded_folders}\n"
            f"Unrecorded files: {self.unrecorded_files}\n"
            f"Recorded but missing folders: {self.recorded_but_missing_folders}\n"
            f"Recorded but missing files: {self.recorded_but_missing_files}\n"
            f"Hash mismatches: {self.hash_mismatches}"
        )

    def check_manifest(self):
        if not os.path.exists(self.manifest_path):
            self.manifest_exists = False
            return
        self.walk_manifest()
        self.walk_base_directory()
        self.check_manifest_files()
    
    def walk_manifest(self):
        for folder_name, subfolders, filenames in os.walk(MANIFEST_ROOT):
            self.manifest_folders.append(folder_name)
            if MANIFEST_FILENAME in filenames:
                self.manifest_folders_with_manifest_file.append(folder_name)
            else:
                self.manifest_folders_with_no_manifest_file.append(folder_name)

    def walk_base_directory(self):
        for folder_name, subfolders, filenames in os.walk(self.base_directory):
            relative_path = os.path.relpath(folder_name, self.base_directory)
            if relative_path.startswith(MANIFEST_ROOT):
                continue
            if relative_path == ".":
                manifest_path = MANIFEST_ROOT
            else:
                manifest_path = os.path.join(MANIFEST_ROOT, relative_path)
            if manifest_path not in self.manifest_folders:
                self.unrecorded_folders.append(relative_path)
                if len(filenames) > 0:
                    self.log_filepaths_as_unrecorded(relative_path, filenames)
            if manifest_path in self.manifest_folders_with_no_manifest_file:
                if len(filenames) > 0:
                    self.log_filepaths_as_unrecorded(relative_path, filenames)

    def log_filepaths_as_unrecorded(self, relative_path, filenames):
        for filename in filenames:
            filepath = os.path.join(relative_path, filename)
            self.unrecorded_files.append(filepath)

    def check_manifest_files(self):
        for folder in self.manifest_folders_with_manifest_file:
            manifest = self.load_manifest(folder)
            matching_folder = os.path.relpath(folder, MANIFEST_ROOT)
            if not os.path.isdir(matching_folder):
                self.recorded_but_missing_folders.append(matching_folder)
            self.check_dictionary(manifest, matching_folder)

    def check_dictionary(self, manifest, folder):
        for filename in manifest:
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                manifest_hash = manifest[filename]
                file_hash = self.hashfile(filepath)
                if manifest_hash != file_hash:
                    self.hash_mismatches.append(filepath)
            else:
                self.recorded_but_missing_files.append(filepath)
        if os.path.isdir(folder):
            with os.scandir(folder) as it:
                for entry in it:
                    if entry.is_file() and entry.name not in manifest:
                        filepath = os.path.join(folder, entry.name)
                        self.unrecorded_files.append(filepath)
    @staticmethod
    def load_manifest(folder):
        filepath = os.path.join(folder, MANIFEST_FILENAME)
        with open(filepath, 'r') as f:
            manifest = json.load(f)
        return manifest

    @staticmethod
    def hashfile(filepath, blocksize = 65536):
        hash_obj = hashlib.sha256()
        with open(filepath, 'rb') as f:
            chunk = f.read(blocksize)
            while len(chunk):
                hash_obj.update(chunk)
                chunk = f.read(blocksize)
        return(hash_obj.hexdigest())


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


date = check_date()
MANIFEST_ROOT = '.manifest'
MANIFEST_FILENAME = f"{date}.json"
cwd = os.getcwd()
manifest = Manifest(cwd)
manifest.check_manifest()
print(manifest)
