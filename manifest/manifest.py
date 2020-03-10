import json
import os
import config
from hash_functions import hashfile

class Manifest():
    def __init__(self, base_directory, manifest_filename):
        self.base_directory = base_directory
        self.manifest_filename = manifest_filename

    def create_manifest_files(self):
        for folder_name, subfolders, filenames in os.walk(self.base_directory):
            relative_path = os.path.relpath(folder_name, self.base_directory)
            if relative_path.startswith(config.MANIFEST_ROOT):
                continue
            manifest = {}
            for filename in filenames:
                filepath = os.path.join(folder_name, filename)
                manifest[filename] = hashfile(filepath)
            if relative_path == ".":
                write_directory = config.MANIFEST_ROOT
            else:
                write_directory = os.path.join(config.MANIFEST_ROOT, relative_path)
            if not os.path.exists(write_directory):
                os.mkdir(write_directory)
            self._write_manifest_file(write_directory, manifest)
            print(folder_name)
        print("Done")

    def _write_manifest_file(self, folder, manifest):
        filepath = os.path.join(folder, self.manifest_filename)
        with open(filepath, 'w') as f:
            json.dump(manifest, f)

class Report():
    def __init__(self, base_directory, manifest_filename):
        self.base_directory = base_directory
        self.manifest_filename = manifest_filename
        self.manifest_path = os.path.join(base_directory, config.MANIFEST_ROOT)
        self.manifest_exists = None
        self.hash_mismatches = []
        self.manifest_folders = []
        self.manifest_folders_with_manifest_file = []
        self.manifest_folders_with_no_manifest_file = []
        self.unrecorded_files = []
        self.unrecorded_folders = []
        self.recorded_but_missing_files = []
        self.recorded_but_missing_folders = []

    def check_manifest(self):
        self.manifest_exists = os.path.exists(self.manifest_path)
        self._walk_manifest()
        self._walk_base_directory()
        self._check_manifest_files()
    
    def _walk_manifest(self):
        for folder_name, subfolders, filenames in os.walk(config.MANIFEST_ROOT):
            self.manifest_folders.append(folder_name)
            if self.manifest_filename in filenames:
                self.manifest_folders_with_manifest_file.append(folder_name)
            else:
                self.manifest_folders_with_no_manifest_file.append(folder_name)

    def _walk_base_directory(self):
        for folder_name, subfolders, filenames in os.walk(self.base_directory):
            relative_path = os.path.relpath(folder_name, self.base_directory)
            if relative_path.startswith(config.MANIFEST_ROOT):
                continue
            if relative_path == ".":
                manifest_path = config.MANIFEST_ROOT
            else:
                manifest_path = os.path.join(config.MANIFEST_ROOT, relative_path)
            if manifest_path not in self.manifest_folders:
                self.unrecorded_folders.append(relative_path)
                if len(filenames) > 0:
                    self._log_filepaths_as_unrecorded(relative_path, filenames)
            if manifest_path in self.manifest_folders_with_no_manifest_file:
                if len(filenames) > 0:
                    self._log_filepaths_as_unrecorded(relative_path, filenames)

    def _log_filepaths_as_unrecorded(self, relative_path, filenames):
        for filename in filenames:
            filepath = os.path.join(relative_path, filename)
            self.unrecorded_files.append(filepath)

    def _check_manifest_files(self):
        for folder in self.manifest_folders_with_manifest_file:
            manifest = self._load_manifest_file(folder)
            matching_folder = os.path.relpath(folder, config.MANIFEST_ROOT)
            if not os.path.isdir(matching_folder):
                self.recorded_but_missing_folders.append(matching_folder)
            self._check_dictionary(manifest, matching_folder)

    def _check_dictionary(self, manifest, folder):
        for filename in manifest:
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                manifest_hash = manifest[filename]
                file_hash = hashfile(filepath)
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

    def _load_manifest_file(self, folder):
        filepath = os.path.join(folder, self.manifest_filename)
        with open(filepath, 'r') as f:
            manifest = json.load(f)
        return manifest
