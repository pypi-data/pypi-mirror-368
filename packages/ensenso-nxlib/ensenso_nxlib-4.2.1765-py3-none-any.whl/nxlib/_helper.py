import os
import pathlib
import platform
import re
import shutil

from nxlib.constants import *
from nxlib.exception import NxLibError
from nxlib.item import NxLibItem


def get_os():
    os_abbreviations = {"Windows": "win",
                        "Linux": "linux",
                        "Darwin": "mac"}
    os_ = platform.system()
    if not os_:
        return "UndeterminedOperatingSystem"
    elif os_ not in os_abbreviations:
        return os_
    return os_abbreviations[os_]


def _get_architecture_bits():
    bits, _ = platform.architecture()
    return bits


def _get_lib_name(is_remote_lib=False):
    if is_remote_lib:
        default_lib_names = {"win32bit": "NxLibRemote32.dll",
                             "win64bit": "NxLibRemote64.dll",
                             "linux32bit": "libNxLibRemote32.so",
                             "linux64bit": "libNxLibRemote64.so"}
    else:
        default_lib_names = {"win32bit": "NxLib32.dll",
                             "win64bit": "NxLib64.dll",
                             "linux32bit": "libNxLib32.so",
                             "linux64bit": "libNxLib64.so"}
    os_ = get_os()
    bits = _get_architecture_bits()

    try:
        return default_lib_names[os_ + bits]
    except KeyError:
        raise NxLibError(f"Unsupported operating system: {bits}-bit {os_}")


def get_lib_path(is_remote_lib=False):
    path = ""
    if "NXLIB_LIBRARY_PATH" in os.environ:
        path = os.environ["NXLIB_LIBRARY_PATH"] + "/"
    return path + _get_lib_name(is_remote_lib)


def get_default_profiler():
    profiler_path = pathlib.Path(NxLibItem()[ITM_PATH][ITM_APPLICATION][ITM_PROFILER].as_string())
    if not profiler_path.is_file():
        raise NxLibError(f"Profiler executable not found in default path: "
                         f"{profiler_path}")
    return profiler_path


def fix_string_encoding(path):
    try:
        if path is None:
            return b''
        path = path.encode()
    except AttributeError:
        pass
    return path


def convert_camel_to_lower_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def convert_camel_to_upper_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()


def fix_nxlib_prefix(word):
    return word[:2] + word[3:]


def unique_numbered_filepath(path, filename_pattern):
    idx = 0
    while path.joinpath(filename_pattern.format(idx)).exists():
        idx += 1
    return path.joinpath(filename_pattern.format(idx))


def is_filepath(filename):
    """
    Returns True if the given filename is a path to a file and not a sole
    filename. foo return False, foo/bar or foo/bar/file.txt returns True.
    """
    if pathlib.Path(filename).name == filename:
        return False
    else:
        return True


def rmdir(path):
    if not path.is_dir():
        return
    shutil.rmtree(path)
