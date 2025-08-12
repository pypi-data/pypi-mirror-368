from pathlib import Path
from subprocess import Popen

import numpy as np

from nxlib import _helper as helper
from nxlib import api
from nxlib.constants import *
from nxlib.item import NxLibItem


NX_LOG_WARNINGS = {
    "NX_LOG_LEVEL_OFF":
    ("Increasing log level from \"Off\" to \"Trace\", otherwise nothing "
     "will be logged by the NxLib."),
    "NX_LOG_OVERFLOW":
    ("A debug buffer overflow occured. Consider incrementing the thread "
     "ring buffer size via [ITM_DEBUG][ITM_BUFFER_SIZE] or a faster buffer "
     "readout."),
    "NX_LOG_IGNORE_NESTED_FILENAME":
    ("Ignoring filename for nested log. Log files are only written for "
     "NxLog objects on first nesting level."),
}


def warn(s):
    if NxLog._print_warnings:
        warning_text = NX_LOG_WARNINGS[s]
        print(f"WARNING: {s}: {warning_text}")


class NxLog:
    """
    This class offers a simple to use interface for logging NxLib events. It
    implements the context manager protocol and thus can be used in a
    ``with`` statement, which encloses the code to be logged. This has the
    nice side effect, that the code to be logged becomes a nested block of code
    that visually contrasts from its surrounding.

    All first-level NxLog objects produce a log file that can be opened with
    NxProfiler. These log files are by default serially numbered and placed in
    a folder named ``enslog/`` relative to the executing script. The output path
    can be changed for all upcoming NxLog objects with the
    :meth:`~set_output_path` method. Resetting the output path is can be done
    by calling the same method with None.

    By default the NxLib log level is ``NX_LOG_LEVEL_TRACE``. It can either be
    set globally for all NxLog instances with the :meth:`~set_log_level` method
    or individually for each instance with the ``level`` parameter in the
    constructor. Note that the ``NX_LOG_LEVEL_OFF`` will be ignored and
    ``NX_LOG_LEVEL_TRACE`` will be used instead, because otherwise nothing
    will be logged.

    NxLog instances can be nested to further increase the granularity of event
    grouping. Each nested ``with`` statement opens a new level of indentation
    and should be called with a block name, otherwise there won't be any
    grouping within the log file.

    Note:
        All nested NxLog objects log to its corresponding first-level/parent
        object, which finally writes the log file to disk when its scope ends.

    If desired, the written log file is automatically opened with the NxProfiler
    executable if the ``open_in_profiler`` parameter of the constructor was set
    to True or the opening was globally enabled with the
    :meth:`enable_open_in_profiler` class method.

    With the :meth:`~write_debug_message` class method user defined debug
    messages can be written to the log. The message will automatically belong to
    the currently open debug block if there is one.

    Args:
        level (str, optional): The NxLib log level. Defaults to
            ``NX_LOG_LEVEL_TRACE``.
        filename (str, optional): The NxLog filename. If none is given, a
            unique serially numbered filename is created. The ``.enslog``
            extension is added if missing.  Defaults to None.
        open_in_profiler (bool, optional): If True, the written log file is
            automatically opened with the NxProfiler executable. Defaults to
            False.
    """
    # -------------------------------------------------------------------------
    # Static variables
    # -------------------------------------------------------------------------
    _parent = None
    _log_level = None
    _default_output_path = Path("enslog/")
    _output_path = _default_output_path
    _open_in_profiler = None
    _print_warnings = True

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------
    def __init__(self, level=None, filename=None, open_in_profiler=False):
        self._parent = self._get_parent()
        self._log_level = self._get_log_level(level)
        self._filename = self._get_filename(filename)
        self._open_in_profiler = self._get_open_in_profiler(open_in_profiler)
        self._content = b''
        self._set_nxlib_log_level()

    # -------------------------------------------------------------------------
    # Implemented protocol methods
    # -------------------------------------------------------------------------
    def __enter__(self):
        # Return self here so that the object assigned by the "as" part of the
        # "with" statement is not None. Necessary for the tests.
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._append_bytes(NxLog.get_debug_buffer())

        # Child exit
        if not self._is_parent():
            return

        # Parent exit
        NxLog._parent = None
        filepath = self._get_filepath()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        self._write_log_file(filepath)
        self._open_profiler(filepath)

    # -------------------------------------------------------------------------
    # Public methods
    # -------------------------------------------------------------------------
    @staticmethod
    def set_log_level(log_level):
        """
        Sets the log level globally for all instances to the given value. Reset
        the log level by either calling this method with ``log_level=None`` or
        ``log_level=NX_LOG_LEVEL_OFF``.

        Args:
            log_level (int): The log level to be set.
        """
        if log_level == NX_LOG_LEVEL_OFF:
            log_level = None
        NxLog._log_level = log_level

    @staticmethod
    def set_output_path(output_path):
        """
        Sets the output path globally for all instances to the given path. Reset
        the output path by calling this method with ``output_path=None``.

        Args:
            output_path (str or pathlib.Path): The output path to be set.
        """
        if output_path is None:
            output_path = NxLog._default_output_path
        NxLog._output_path = Path(output_path)

    @staticmethod
    def enable_open_in_profiler():
        """
        Enables automatic opening of the created log files with NxProfiler.
        """
        NxLog._open_in_profiler = True

    @staticmethod
    def disable_open_in_profiler():
        """
        Disables automatic opening of the created log files with NxProfiler.
        """
        NxLog._open_in_profiler = None

    @staticmethod
    def enable_warnings():
        """ Enables printing of warnings. """
        NxLog._print_warnings = True

    @staticmethod
    def disable_warnings():
        """ Disables printing of warnings. """
        NxLog._print_warnings = False

    @staticmethod
    def write_debug_message(message):
        """
        Inserts a user defined debug message into the NxLib debug stream. The
        message will belong to the last opened debug block if there is any.

        Args:
            message (str): The message to be written.
        """
        api.write_debug_message(message)

    @staticmethod
    def get_debug_buffer():
        """
        This method uses :func:`nxlib.api.get_debug_buffer` to retrieve all
        bytes from the debug buffer. Therefore the API function is called twice,
        once to determine the number of bytes held by the debug buffer and a
        second time to actually read and clear the debug buffer.

        Note:
            A warning is printed if the debug buffer overflowed and warnings
            are enabled. In this case the debug buffer size should be increased
            via the tree item :doc:`/Debug/BacklogSize <tree:debug/backlogsize>`.

        Returns:
            bytes: The debug buffers content as bytes.
        """
        buffer_size = 0
        for clear_read in [np.int32(0), np.int32(1)]:
            buffer = np.zeros(buffer_size, dtype=np.uint8, order="C")
            cbuffer = np.ctypeslib.as_ctypes(buffer)
            _, buffer_size, overflow = api.get_debug_buffer(
                cbuffer, buffer_size, clear_read)
        if overflow:
            warn("NX_LOG_OVERFLOW")
        return buffer.tobytes()

    # -------------------------------------------------------------------------
    # Private methods
    # -------------------------------------------------------------------------
    def _get_parent(self):
        if NxLog._parent is None:
            NxLog._parent = self
        return NxLog._parent

    def _is_parent(self):
        return self == NxLog._parent

    def _get_log_level(self, level):
        if level:
            if level == NX_LOG_LEVEL_OFF:
                warn("NX_LOG_LEVEL_OFF")
                level = NX_LOG_LEVEL_TRACE
            return level
        elif NxLog._log_level:
            return NxLog._log_level
        else:
            return NX_LOG_LEVEL_TRACE

    def _set_nxlib_log_level(self):
        NxLibItem()[ITM_DEBUG][ITM_LEVEL].set_string(self._log_level)

    def _get_filename(self, filename):
        if filename is None:
            return None
        if filename and not self._is_parent():
            warn("NX_LOG_IGNORE_NESTED_FILENAME")
        # Strip trailing slashes regardless of the OS.
        return str(Path(filename))

    def _get_open_in_profiler(self, open_in_profiler):
        if open_in_profiler or NxLog._open_in_profiler:
            return True
        else:
            return False

    def _append_bytes(self, bytes_):
        if self._is_parent():
            self._content += bytes_
        else:
            self._parent._append_bytes(bytes_)

    def _get_default_filepath(self):
        pattern = "temp-{:04d}.enslog"
        return helper.unique_numbered_filepath(self._output_path, pattern)

    def _get_filepath(self):
        if self._filename is None:
            return self._get_default_filepath()

        if helper.is_filepath(self._filename):
            return Path(self._filename)

        filepath = NxLog._output_path.joinpath(self._filename)
        if not filepath.suffix == ".nxlog" or not filepath.suffix == ".enslog":
            filepath = filepath.with_suffix(".enslog")
        return filepath

    def _write_log_file(self, filepath):
        with filepath.open(mode="wb") as f:
            f.write(self._content)

    def _open_profiler(self, filepath):
        if self._open_in_profiler:
            cmd = f"{helper.get_default_profiler().resolve()} {str(filepath)}"
            Popen(cmd.split())


class NxDebugBlock(NxLog):
    """
    This class offers a simple to use interface for opening an NxLib debug
    block. It is derived from the :class:`nxlib.log.NxLog` class and thus can be
    used as this to create a log file. It also implements the context manager
    protocol and thus can be used in a ``with`` statement, which encloses the
    code to be logged. This has the nice side effect, that the code to be logged
    becomes a nested block of code that visually contrasts from its surrounding.

    Args:
        name (str, optional): The name of the debug block. Defaults to None.
        level (str, optional): The NxLib log level. Defaults to
            ``NX_LOG_LEVEL_TRACE``.
        filename (str, optional): The NxLog filename. If none is given, a
            unique serially numbered filename is created. The ``.enslog``
            extension is added if missing.  Defaults to None.
        open_in_profiler (bool, optional): If True, the written log file is
            automatically opened with the NxProfiler executable. Defaults to
            False.
    """
    def __init__(self, name, level=None, filename=None, open_in_profiler=False):
        super().__init__(level, filename, open_in_profiler)
        self._name = name

    def __enter__(self):
        api.open_debug_block(self._name, self._log_level)
        # Return self here so that the object assigned by the "as" part of the
        # "with" statement is not None. Necessary for the tests.
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        api.close_debug_block()
        super().__exit__(exc_type, exc_value, exc_tb)
