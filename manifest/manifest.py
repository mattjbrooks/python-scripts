import datetime
import hashlib
import json
import os
import config


class Manifest():
    def __init__(self, base_directory=os.getcwd(), manifest_filename=None):
        self.base_directory = base_directory
        self.manifest_filename = f"{current_date()}.json" if (manifest_filename
                == None) else manifest_filename

    def create_manifest(self):
        for folder_name, subfolders, filenames in os.walk(self.base_directory):
            relative_path = os.path.relpath(folder_name, self.base_directory)
            if relative_path.startswith(config.MANIFEST_ROOT):
                continue
            manifest = {}
            for filename in filenames:
                filepath = os.path.join(folder_name, filename)
                manifest[filename] = hashfile(filepath)
            if relative_path == '.':
                write_directory = config.MANIFEST_ROOT
            else:
                write_directory = os.path.join(config.MANIFEST_ROOT, relative_path)
            if not os.path.exists(write_directory):
                os.mkdir(write_directory)
            self._write_manifest_file(write_directory, manifest)
            print(folder_name)
        print("Done")

    def delete_manifest(self):
        if not self.manifest_filename.endswith(".json"):
            raise ValueError(
                    f"Non-manifest filename {self.manifest_filename}"
                    f" passed for deletion")
        if not os.path.isdir(config.MANIFEST_ROOT):
            print("Manifest directory not found")
            return
        manifest_exists = False
        for folder_name, subfolders, filenames in os.walk(config.MANIFEST_ROOT):
            if self.manifest_filename in filenames:
                manifest_exists = True
                filepath = os.path.join(folder_name, self.manifest_filename)
                try:
                    os.unlink(filepath)
                    print(f"Deleting {filepath}")
                except:
                    print(f"Error while deleting {filepath}")
        if not manifest_exists:
            print(f"{self.manifest_filename} not found in manifest directory")
            return
        folders_without_files = []
        for folder_name, subfolders, filenames in os.walk(config.MANIFEST_ROOT):
            if len(filenames) == 0:
                folders_without_files.append(folder_name)
        folders_without_files.sort(key=len, reverse=True)
        for folder in folders_without_files:
            if len(os.listdir(folder)) == 0:
                try:
                    os.rmdir(folder)
                    print(f"Deleting {folder}")
                except:
                    print(f"Error while deleting directory {folder}")
        print("Done")

    def _write_manifest_file(self, folder, manifest):
        filepath = os.path.join(folder, self.manifest_filename)
        with open(filepath, 'w') as f:
            json.dump(manifest, f)


class Report():
    def __init__(self, base_directory=os.getcwd(), manifest_filename=None):
        self.base_directory = base_directory
        self.manifest_filename = f"{current_date()}.json" if (manifest_filename
                == None) else manifest_filename
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
        self._check_manifest()

    def __str__(self):
        return '\n'.join(
                [f"{key}: {value}" for key, value in self.__dict__.items()])

    def log(self, color=False):
        ANSI_cyan = "\x1b[36m"
        ANSI_green = "\x1b[32m"
        ANSI_red = "\x1b[31m"
        ANSI_reset = "\x1b[0m"
        on = ANSI_cyan if color else ""
        ok = ANSI_green if color else ""
        warn = ANSI_red if color else ""
        off = ANSI_reset if color else ""
        if not os.path.exists(self.manifest_path):
            msg = (
                    f"Looking for {on}{self.manifest_path}{off}\n"
                    f"Manifest directory not found"
            )
            return msg
        if not self.manifest_exists:
            msg = (
                    f"Checking {on}{self.manifest_path}{off} for instances of "
                    f"{on}{self.manifest_filename}{off}\n"
                    f"Manifest file(s) not found"
            )
            return msg
        manifest_errors = '\n'.join(self.manifest_folders_with_no_manifest_file)
        unrecorded_files = '\n'.join(self.unrecorded_files)
        unrecorded_folders = '\n'.join(self.unrecorded_folders)
        missing_files = '\n'.join(self.recorded_but_missing_files)
        missing_folders = '\n'.join(self.recorded_but_missing_folders)
        hash_mismatches = '\n'.join(self.hash_mismatches)
        msg = ""
        if unrecorded_files:
            msg += f"{on}Unrecorded files:{off}\n{unrecorded_files}\n"
        if unrecorded_folders:
            msg += f"{on}Unrecorded folders:{off}\n{unrecorded_folders}\n"
        if missing_files:
            msg +=  f"{on}Missing files:{off}\n{missing_files}\n"
        if missing_folders:
            msg += f"{on}Missing folders:{off}\n{missing_folders}\n"
        if hash_mismatches:
            msg += f"{on}Hash mismatches:{off}\n{hash_mismatches}\n"
        if manifest_errors:
            plural = 's' if len(self.manifest_folders_with_no_manifest_file) > 1 else ""
            msg += (
                    f"{warn}WARNING: Manifest error - "
                    f"no manifest file for folder{plural}:{off}\n"
                    f"{manifest_errors}"
            )
        msg = msg.rstrip('\n')
        if not msg:
            msg = f"No issues found - {ok}matches manifest{off}"
        return msg

    def _check_manifest(self):
        if os.path.exists(self.manifest_path):
            self._walk_manifest()
            self._walk_base_directory()
            self._check_manifest_files()

    def _walk_manifest(self):
        self.manifest_exists = False
        for folder_name, subfolders, filenames in os.walk(config.MANIFEST_ROOT):
            self.manifest_folders.append(folder_name)
            if self.manifest_filename in filenames:
                self.manifest_folders_with_manifest_file.append(folder_name)
                self.manifest_exists = True
            else:
                self.manifest_folders_with_no_manifest_file.append(folder_name)

    def _walk_base_directory(self):
        for folder_name, subfolders, filenames in os.walk(self.base_directory):
            relative_path = os.path.relpath(folder_name, self.base_directory)
            if relative_path.startswith(config.MANIFEST_ROOT):
                continue
            if relative_path == '.':
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


def current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def hashfile(filepath, blocksize = 65536):
    hash_obj = hashlib.sha256()
    with open(filepath, 'rb') as f:
        chunk = f.read(blocksize)
        while len(chunk):
            hash_obj.update(chunk)
            chunk = f.read(blocksize)
    return(hash_obj.hexdigest())
