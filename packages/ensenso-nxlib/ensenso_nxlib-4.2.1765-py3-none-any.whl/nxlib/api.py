import atexit
import os
from ctypes import CDLL, POINTER
from ctypes import byref, c_char_p, c_double, c_int32, c_void_p, cast

import _ctypes

from nxlib import _helper as helper
from nxlib.constants import *
from nxlib.exception import NxLibError, NxLibException


__all__ = [
    "close_tcp_port",
    "connect",
    "disconnect",
    "erase",
    "finalize",
    "get_binary",
    "get_binary_info",
    "get_bool",
    "get_count",
    "get_debug_buffer",
    "get_debug_messages",
    "get_double",
    "get_int",
    "get_json",
    "get_json_meta",
    "get_name",
    "get_string",
    "get_type",
    "initialize",
    "is_current_lib_remote",
    "load_lib",
    "load_remote_lib",
    "make_unique_item",
    "open_tcp_port",
    "set_binary",
    "set_binary_formatted",
    "set_bool",
    "set_double",
    "set_int",
    "set_json",
    "set_null",
    "set_string",
    "translate_error_code",
    "wait_for_bool_value",
    "wait_for_change",
    "wait_for_double_value",
    "wait_for_int_value",
    "wait_for_string_value",
    "wait_for_type",
]


class _Nxlib():
    def __init__(self):
        self.is_remote = False
        self.is_connected = False
        self.lib_object = None
        atexit.register(self.reset)

    def reset(self):
        if self.lib_object is None:
            return
        try:
            if self.is_remote:
                disconnect()
            else:
                finalize()
        except NxLibException:
            # Ignore any errors while finalizing the NxLib. We will unload the
            # library anyway.
            pass

        # ctypes does not unload the library even when the CDLL object gets
        # garbage collected, so we unload it manually.
        if os.name == "posix":
            _ctypes.dlclose(self.lib_object._handle)
        elif os.name == "nt":
            _ctypes.FreeLibrary(self.lib_object._handle)

        del self.lib_object
        self.lib_object = None

    def __del__(self):
        try:
            self.reset()
        except NxLibException:
            # Sometimes we cannot clean up the library when unloading the
            # module, because some things that are needed for the destruction
            # are already unloaded. Ignore any errors this might cause.
            pass


# testing flag
__nx_testing__ = False

# global placeholder for the nxlib_instance
_nxlib = None

# Instance ID that is incremented with each `initialize`. Used to determine
# which instance a temporary node belongs to.
_nxlib_id = 0


def _get_lib(path=None):
    # will default load the normal nxlib, if there has been no
    # load_remote_lib beforehand!
    global _nxlib

    if _nxlib is None:
        _nxlib = _Nxlib()

    if _nxlib.lib_object is None:
        if _nxlib.is_remote:
            load_remote_lib(path)
        else:
            load_lib(path)
    return _nxlib.lib_object


def is_current_lib_remote():
    """
    Checks whether the currently loaded NxLib library is a remote NxLib.

    Returns:
        bool: True if the currently loaded NxLib library is a remote NxLib.
        False otherwise.
    """
    # For Testing and debug purpose
    global _nxlib
    if _nxlib is None:
        return False
    return _nxlib.is_remote


def load_lib(path=None):
    """
    Loads the default or given NxLib.

    Args:
        path (str, optional): Filepath to the shared library. Defaults to None.

    Raises:
        `nxlib.NxLibError`: If the shared library could not be loaded.
    """
    global _nxlib

    if _nxlib is None:
        _nxlib = _Nxlib()

    _nxlib.reset()

    if path is None:
        _nxlib.lib_object = CDLL(helper.get_lib_path())
    else:
        _nxlib.lib_object = CDLL(path)
    _nxlib.is_remote = False
    if _nxlib.lib_object is None:
        raise NxLibError("Could not load shared library")


def load_remote_lib(path=None):
    """
    Loads the default or given remote NxLib.

    Args:
        path (str, optional): Filepath to the shared remote library.
            Defaults to None.

    Raises:
        `nxlib.NxLibError`: If the shared remote library could not be loaded.
    """
    global _nxlib

    if _nxlib is None:
        _nxlib = _Nxlib()

    _nxlib.reset()

    if path is None:
        _nxlib.lib_object = CDLL(helper.get_lib_path(is_remote_lib=True))
    else:
        _nxlib.lib_object = CDLL(path)
    _nxlib.is_remote = True
    _nxlib.is_connected = False
    if _nxlib.lib_object is None:
        raise NxLibError("Could not load shared remote library")


def _check_return_code(path="", return_code=c_int32(0)):
    if isinstance(return_code, c_int32):
        return_code = return_code.value
    if return_code != NXLIB_OPERATION_SUCCEEDED:
        if isinstance(path, bytes):
            path = path.decode()
        raise NxLibException(path, return_code)


def _check_string(s):
    if s is not None:
        return s.decode()
    return None


def _set(f, path, value):
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    f(byref(return_code), path, value)
    _check_return_code(path, return_code)


def set_null(path):
    f = _get_lib().nxLibSetNull
    f.argtypes = [POINTER(c_int32), c_char_p]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    f(byref(return_code), path)
    _check_return_code(path, return_code)


def set_int(path, value):
    f = _get_lib().nxLibSetInt
    f.argtypes = [POINTER(c_int32), c_char_p, c_int32]
    _set(f, path, value)


def set_double(path, value):
    f = _get_lib().nxLibSetDouble
    f.argtypes = [POINTER(c_int32), c_char_p, c_double]
    _set(f, path, value)


def set_bool(path, value):
    f = _get_lib().nxLibSetBool
    f.argtypes = [POINTER(c_int32), c_char_p, c_int32]
    _set(f, path, value)


def set_string(path, value):
    f = _get_lib().nxLibSetString
    f.argtypes = [POINTER(c_int32), c_char_p, c_char_p]
    value = helper.fix_string_encoding(value)
    _set(f, path, value)


def set_json(path, value, only_writeable_nodes=False):
    f = _get_lib().nxLibSetJson
    f.argtypes = [POINTER(c_int32), c_char_p, c_char_p, c_int32]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    value = helper.fix_string_encoding(value)
    f(byref(return_code), path, value, only_writeable_nodes)
    _check_return_code(path, return_code)


def set_binary(path, buffer, buffer_size):
    f = _get_lib().nxLibSetBinary
    f.argtypes = [POINTER(c_int32), c_char_p, POINTER(c_void_p), c_int32]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    buffer = cast(buffer, POINTER(c_void_p))
    f(byref(return_code), path, buffer, buffer_size)
    _check_return_code(path, return_code)


def set_binary_formatted(path, buffer, width, height, channel_count,
                         bytes_per_element, is_float):
    f = _get_lib().nxLibSetBinaryFormatted
    f.argtypes = [
        POINTER(c_int32), c_char_p,
        POINTER(c_void_p), c_int32, c_int32, c_int32, c_int32, c_int32
    ]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    buffer = cast(buffer, POINTER(c_void_p))
    f(byref(return_code), path, buffer, width, height, channel_count,
      bytes_per_element, is_float)
    _check_return_code(path, return_code)


def get_binary(path, buffer, buffer_size):
    f = _get_lib().nxLibGetBinary
    f.argtypes = [
        POINTER(c_int32), c_char_p,
        POINTER(c_void_p), c_int32,
        POINTER(c_int32),
        POINTER(c_double)
    ]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    buffer = cast(buffer, POINTER(c_void_p))
    bytes_copied = c_int32(0)
    timestamp = c_double(0)
    f(byref(return_code), path, buffer, buffer_size, byref(bytes_copied),
      byref(timestamp))
    _check_return_code(path, return_code)
    return bytes_copied.value, timestamp.value


def get_binary_info(path):
    f = _get_lib().nxLibGetBinaryInfo
    f.argtypes = [
        POINTER(c_int32), c_char_p,
        POINTER(c_int32),
        POINTER(c_int32),
        POINTER(c_int32),
        POINTER(c_int32),
        POINTER(c_int32),
        POINTER(c_double)
    ]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    width = c_int32(0)
    height = c_int32(0)
    channel_count = c_int32(0)
    bytes_per_element = c_int32(0)
    is_float = c_int32(0)
    timestamp = c_double(0)
    f(byref(return_code), path, byref(width), byref(height),
      byref(channel_count), byref(bytes_per_element), byref(is_float),
      byref(timestamp))
    _check_return_code(path, return_code)
    return (width.value, height.value, channel_count.value,
            bytes_per_element.value, is_float.value == 1, timestamp.value)


def has_path(path):
    return_code = c_int32(0)
    type_ = get_type(path, return_code)
    if return_code.value == NXLIB_OPERATION_SUCCEEDED:
        # Item type can still be invalid.
        return type_ != NXLIB_ITEM_TYPE_INVALID
    elif return_code.value == NXLIB_ITEM_INEXISTENT:
        return False
    # Otherwise raise an execption.
    _check_return_code(path, return_code)


def _get(f, path, return_code=None):
    return_code_ = c_int32(0)
    path = helper.fix_string_encoding(path)
    result = f(byref(return_code_), path)
    if return_code is not None:
        return_code = return_code_
    else:
        _check_return_code(path, return_code_)
    return result


def get_type(path, return_code=None):
    f = _get_lib().nxLibGetType
    f.restype = c_int32
    f.argtypes = [POINTER(c_int32), c_char_p]
    return _get(f, path, return_code)


def get_int(path):
    f = _get_lib().nxLibGetInt
    f.restype = c_int32
    f.argtypes = [POINTER(c_int32), c_char_p]
    return _get(f, path)


def get_bool(path):
    f = _get_lib().nxLibGetBool
    f.restype = c_int32
    f.argtypes = [POINTER(c_int32), c_char_p]
    return bool(_get(f, path))


def get_count(path):
    f = _get_lib().nxLibGetCount
    f.restype = c_int32
    f.argtypes = [POINTER(c_int32), c_char_p]
    return _get(f, path)


def get_double(path):
    f = _get_lib().nxLibGetDouble
    f.restype = c_double
    f.argtypes = [POINTER(c_int32), c_char_p]
    return _get(f, path)


def get_string(path):
    f = _get_lib().nxLibGetString
    f.restype = c_char_p
    f.argtypes = [POINTER(c_int32), c_char_p]
    return _check_string(_get(f, path))


def get_name(path):
    f = _get_lib().nxLibGetName
    f.restype = c_char_p
    f.argtypes = [POINTER(c_int32), c_char_p]
    return _check_string(_get(f, path))


def get_json(path, pretty_print, number_precision, scientific_number_format):
    f = _get_lib().nxLibGetJson
    f.restype = c_char_p
    f.argtypes = [POINTER(c_int32), c_char_p, c_int32, c_int32, c_int32]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    result = f(byref(return_code), path, pretty_print, number_precision,
               scientific_number_format)
    _check_return_code(path, return_code)
    return _check_string(result)


def get_json_meta(path, num_levels, pretty_print, number_precision,
                  scientific_number_format):
    f = _get_lib().nxLibGetJsonMeta
    f.restype = c_char_p
    f.argtypes = [
        POINTER(c_int32), c_char_p, c_int32, c_int32, c_int32, c_int32
    ]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    result = f(byref(return_code), path, num_levels, pretty_print,
               number_precision, scientific_number_format)
    _check_return_code(path, return_code)
    return _check_string(result)


def erase(path):
    f = _get_lib().nxLibErase
    f.argtypes = [POINTER(c_int32), c_char_p]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    f(byref(return_code), path)
    if return_code.value == NXLIB_ITEM_INEXISTENT:
        return
    _check_return_code(path, return_code)


def wait_for_change(path):
    f = _get_lib().nxLibWaitForChange
    f.argtypes = [POINTER(c_int32), c_char_p]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    f(byref(return_code), path)
    _check_return_code(path, return_code)


def wait_for_type(path, awaited_type, wait_for_equal):
    f = _get_lib().nxLibWaitForType
    f.argtypes = [POINTER(c_int32), c_char_p, c_int32, c_int32]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    f(byref(return_code), path, awaited_type, wait_for_equal)
    _check_return_code(path, return_code)


def wait_for_int_value(path, value, wait_for_equal):
    f = _get_lib().nxLibWaitForIntValue
    f.argtypes = [POINTER(c_int32), c_char_p, c_int32, c_int32]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    f(byref(return_code), path, value, wait_for_equal)
    _check_return_code(path, return_code)


def wait_for_string_value(path, value, wait_for_equal):
    f = _get_lib().nxLibWaitForStringValue
    f.argtypes = [POINTER(c_int32), c_char_p, c_char_p, c_int32]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    value = helper.fix_string_encoding(value)
    f(byref(return_code), path, value, wait_for_equal)
    _check_return_code(path, return_code)


def wait_for_double_value(path, value, wait_for_equal):
    f = _get_lib().nxLibWaitForDoubleValue
    f.argtypes = [POINTER(c_int32), c_char_p, c_double, c_int32]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    f(byref(return_code), path, value, wait_for_equal)
    _check_return_code(path, return_code)


def wait_for_bool_value(path, value, wait_for_equal):
    f = _get_lib().nxLibWaitForBoolValue
    f.argtypes = [POINTER(c_int32), c_char_p, c_int32, c_int32]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    f(byref(return_code), path, value, wait_for_equal)
    _check_return_code(path, return_code)


def make_unique_item(path, item_name):
    f = _get_lib().nxLibMakeUniqueItem
    f.restype = c_char_p
    f.argtypes = [POINTER(c_int32), c_char_p, c_char_p]
    return_code = c_int32(0)
    path = helper.fix_string_encoding(path)
    item_name = helper.fix_string_encoding(item_name)
    result = f(byref(return_code), path, item_name)
    _check_return_code(return_code=return_code)
    return _check_string(result)


def translate_error_code(error_code):
    """
    Returns the corresponding error text for the given NxLib error code.

    Args:
        error_code (int): The error code.

    Returns:
        str: The corresponding error text.
    """
    if error_code < 0 or error_code > len(NX_ERRORS):
        return ''
    return NX_ERRORS[error_code]


def get_debug_messages():
    f = _get_lib().nxLibGetDebugMessages
    f.restype = c_char_p
    f.argtypes = [POINTER(c_int32)]
    return_code = c_int32(0)
    result = f(byref(return_code))
    _check_return_code(return_code=return_code)
    return _check_string(result)


def get_debug_buffer(destination_buffer, buffer_size, clear_read):
    """
    Copy n=buffer_size bytes of the NxLib debug buffer into the given
    destination buffer and clear the debug buffer if desired.

    Args:
        destination_buffer (``Object``): The byte buffer the debug buffer's
            content gets written to.
        buffer_size (int): The buffer size.
        clear_read (bool): If True, the buffer will be cleared after reading.

    Raises:
        NxLibException: If the wrapped NxLib function returned with an error.

    Returns:
        tuple containing

        * bytes_read (int): The number of bytes read from the debug buffer.
        * bytes_remaining (int): The number of bytes remaining in the debug
          buffer.
        * overflow (bool): True if the debug buffer overflowed before it was
          read. False otherwise.
    """
    f = _get_lib().nxLibGetDebugBuffer
    f.restype = c_int32
    f.argtypes = [
        POINTER(c_int32),
        POINTER(c_void_p), c_int32,
        POINTER(c_int32), c_int32
    ]
    return_code = c_int32(0)
    destination_buffer = cast(destination_buffer, POINTER(c_void_p))
    bytes_remaining = c_int32(0)
    clear_read = c_int32(clear_read)
    bytes_read = f(byref(return_code), destination_buffer, buffer_size,
                   byref(bytes_remaining), clear_read)
    overflow = False
    if return_code.value == NXLIB_DEBUG_MESSAGE_OVERFLOW:
        overflow = True
    else:
        _check_return_code(return_code=return_code)
    return bytes_read, bytes_remaining.value, overflow


def _log_level_str_to_int(level):
    if level not in NX_LOG_LEVELS:
        return 0
    return NX_LOG_LEVELS[level]


def open_debug_block(block_name, level):
    f = _get_lib().nxLibOpenDebugBlock
    f.argtypes = [POINTER(c_int32), c_char_p, c_int32]
    return_code = c_int32(0)
    block_name = helper.fix_string_encoding(block_name)
    level = _log_level_str_to_int(level)
    f(byref(return_code), block_name, level)
    _check_return_code(return_code=return_code)


def close_debug_block():
    f = _get_lib().nxLibCloseDebugBlock
    f.argtypes = [POINTER(c_int32)]
    return_code = c_int32(0)
    f(byref(return_code))
    _check_return_code(return_code=return_code)


def write_debug_message(message):
    f = _get_lib().nxLibWriteDebugMessage
    f.argtypes = [POINTER(c_int32), c_char_p]
    return_code = c_int32(0)
    message = helper.fix_string_encoding(message)
    f(byref(return_code), message)
    _check_return_code(return_code=return_code)


def initialize(wait_for_initial_camera_refresh=True, path=None):
    """
    Explicitly initializes the library and starts to enumerate the connected
    cameras. When omitting this function call, the library is initialized on
    first access to the tree.

    Note:
        After :func:`finalize` was called, the library will no longer be
        initialized automatically when you access the tree. You can reinitialize
        it by explicitly calling :func:`~initialize`.

    Args:
        wait_for_initial_camera_refresh (bool, optional): Specifies whether to
            wait for all cameras to be enumerated or to return immediately.
            Defaults to True.

    Raises:
        `nxlib.NxLibError`: If the currently loaded NxLib library is a remote
            NxLib.
    """
    if is_current_lib_remote():
        raise NxLibError("Library is a remote NxLib. Only normal NxLib "
                         "instances can use initialize.")
    f = _get_lib(path).nxLibInitialize
    f.argtypes = [POINTER(c_int32), c_int32]
    return_code = c_int32(0)
    f(byref(return_code), wait_for_initial_camera_refresh)
    _check_return_code(return_code=return_code)
    global _nxlib_id
    _nxlib_id += 1


def finalize():
    """
    Explicitly closes the library, terminating all internal threads and freeing
    allocated memory. It is important to explicitly call :func:`~finalize`
    before unloading the NxLib library when your process is not terminating
    afterwards, because Windows doesn't allow to cleanly exit threads during DLL
    unload.

    Raises:
        `nxlib.NxLibError`: If the currently loaded NxLib library is a remote
            NxLib.
    """
    if _nxlib is None or _nxlib.lib_object is None:
        return
    if is_current_lib_remote():
        raise NxLibError("Library is a remote NxLib. Only normal NxLib "
                         "instances can use finalize.")
    f = _get_lib().nxLibFinalize
    f.argtypes = [POINTER(c_int32)]
    return_code = c_int32(0)
    f(byref(return_code))
    _check_return_code(return_code=return_code)


def open_tcp_port(port_number=0, opened_port=0):
    """
    Opens a TCP port on which a remote NxLib can connect to the current NxLib
    instance.

    Args:
        port_number (int, optional): The port to be opened. Specify 0 here to
            automatically choose a port in the range 24000 to 25000.
            Defaults to 0.
        opened_port (int, optional): The variable receiving the opened port
            number. Defaults to 0.

    Raises:
        `nxlib.NxLibError`: If the currently loaded NxLib library is a remote
            NxLib.
    """
    if is_current_lib_remote():
        raise NxLibError("Library is a remote NxLib. Only normal NxLib "
                         "instances are allowed to open TCP ports.")
    f = _get_lib().nxLibOpenTcpPort
    f.argtypes = [POINTER(c_int32), c_int32, c_int32]
    return_code = c_int32(0)
    f(byref(return_code), port_number, opened_port)
    _check_return_code(return_code=return_code)
    if __nx_testing__:
        print(port_number)


def close_tcp_port():
    """
    Disconnects all connected NxLibRemote instances and closes the opened TCP
    port, if any.

    Raises:
        `nxlib.NxLibError`: If the currently loaded NxLib library is a remote
            NxLib.
    """
    if is_current_lib_remote():
        raise NxLibError("Library is a remote NxLib. Only normal NxLib "
                         "instances are allowed to close TCP ports.")
    f = _get_lib().nxLibCloseTcpPort
    return_code = c_int32(0)
    f.argtypes = [POINTER(c_int32)]
    f(byref(return_code))
    _check_return_code(return_code=return_code)


def connect(hostname, port):
    """
    Remote NxLib specific function that opens a connection to the remote NxLib
    with the given hostname and port.

    Args:
        hostname (str): The hostname of the remote NxLib to connect to.
        port (int): The port of the remote NxLib to connect to.

    Raises:
        `nxlib.NxLibError`: If the currently loaded NxLib library is not a
            remote NxLib.
    """
    if not is_current_lib_remote():
        raise NxLibError("Cannot use connect function from a normal NxLib.")
    f = _get_lib().nxLibConnect
    f.argtypes = [POINTER(c_int32), c_char_p, c_int32]
    return_code = c_int32(0)
    hostname = helper.fix_string_encoding(hostname)
    f(byref(return_code), hostname, port)
    _check_return_code(return_code=return_code)
    _nxlib.is_connected = True


def disconnect():
    """
    Remote NxLib specific function that closes the connection to the remote
    NxLib.

    Raises:
        `nxlib.NxLibError`: If the currently loaded NxLib library is not a
            remote NxLib.
    """
    if not is_current_lib_remote():
        raise NxLibError("Cannot use disconnenct function from a normal "
                         "NxLib.")
    f = _get_lib().nxLibDisconnect
    f.argtypes = [POINTER(c_int32)]
    return_code = c_int32(0)
    f(byref(return_code))
    _check_return_code(return_code=return_code)
    _nxlib.is_connected = False
