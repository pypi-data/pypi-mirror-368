import nxlib.api as api
from nxlib.constants import *
from nxlib.exception import NxLibException
from nxlib.item import NxLibItem

__all__ = ["NxLibCommand"]


class NxLibCommand:
    """
    This class simplifies the execution of NxLib commands. The
    :meth:`~parameters` and :meth:`~result` methods provide access to the
    corresponding ``Parameters`` and ``Result`` nodes of the tree. The
    :meth:`~execute` method starts the command by writing the command name to
    the tree and allows for synchronous and asynchronous command execution.

    Args:
        command_name (str): Name of the command to execute.
        node_name (str, optional): Name of the execution ``slot`` the command
            should run in. By default the class will create a temporary slot
            used only by this instance of :class:`NxLibCommand`, which is
            automatically deleted in the destructor.
    """
    def __init__(self, command_name, node_name=None, params={}):
        self._command_name = command_name
        self._remove_slot_on_destruction = False
        self._nxlib_id = api._nxlib_id

        if node_name is None:
            self._create_temporary_slot()
        else:
            self._command_item = NxLibItem()[ITM_EXECUTE][node_name]

        self.parameters() << params

    def _belongs_to_current_lib(self):
        return self._nxlib_id == api._nxlib_id

    def _remove_slot(self):
        if self._remove_slot_on_destruction and self._belongs_to_current_lib():
            try:
                if not api.is_current_lib_remote() or api._nxlib.is_connected:
                    self._command_item.erase()
            except NxLibException as e:
                if e.get_error_code() == NXLIB_INITIALIZATION_NOT_ALLOWED:
                    pass
                else:
                    raise e
        self._remove_slot_on_destruction = False

    def __del__(self):
        try:
            self._remove_slot()
        except Exception:
            # The destructor might be called after some of the required modules
            # have already been unloaded. Ignore any errors this might cause.
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # We keep the slot if an exception occured within the context, because
        # the command is referenced by the exception and might be used for error
        # investigation. The command destruction is eventually triggered after
        # the exception gets destroyed.
        if exc_type is None:
            self._remove_slot()

    def _create_temporary_slot(self, base_name=None):
        self._command_item = NxLibItem()[ITM_EXECUTE].make_unique_item(
            base_name)
        self._remove_slot_on_destruction = True

    def slot(self):
        """
        The slot, i.e. the NxLibItem, the NxLibCommand is running on.

        Returns:
            ``NxLibItem``: The NxLibItem the command runs on.
        """
        return self._command_item

    def parameters(self):
        """
        The command's ``Parameters`` node, that will be fetched before the
        command executes.

        Returns:
            ``NxLibItem``: The NxLibItem in which the parameters are stored.
        """
        return self.slot()[ITM_PARAMETERS]

    def result(self):
        """
        The command's ``Result`` node after the command finishes.

        Returns:
            ``NxLibItem``: The NxLibItem in which the results are stored.
        """
        return self.slot()[ITM_RESULT]

    def successful(self):
        """
        Checks whether the previous command execution was successful.

        Returns:
            bool: True if the previous NxLib command execution was successful,
            i.e. there is no ``ErrorSymbol`` node under the ``Result`` node.
            False otherwise.
        """
        return not self.result()[ITM_ERROR_SYMBOL].exists()

    def execute(self, command_name=None, wait=True):
        """
        Executes the current command.

        Args:
            command_name (str, optional): Name of the command to execute. This
                overwrites the command name from the constructor. Defaults to
                None.
            wait (bool, optional): If True, the function waits until execution
                of the command is finished and throws an NxLibException if the
                command finished with an error. Defaults to True.
        """
        if not command_name:
            command_name = self._command_name

        function_item = self.slot()[ITM_COMMAND]
        function_item.set_string(command_name)

        if wait:
            self.wait()

    def finished(self):
        """
        Checks whether the command execution has already finished.

        Returns:
            bool: True, if NxLib is not currently executing a command, i.e. the
            ``Command`` node is not exisintg or is Null. False otherwise.
        """
        cmd_node = self.slot()[ITM_COMMAND]
        return (not cmd_node.exists() or cmd_node.is_null())

    def wait(self):
        """
        Waits for the command execution to finish.

        Raises:
            NxLibException: If the command execution was not successful.
        """
        function_item = self.slot()[ITM_COMMAND]
        if not function_item.exists():
            return
        function_item.wait_for_type(NXLIB_ITEM_TYPE_NULL, True)
        self.assert_successful()

    def assert_successful(self):
        """
        Checks whether the previous command execution is finished and was
        successful.

        Raises:
            NxLibException: If the command execution was not successful.
        """
        if not self.finished() or not self.successful():
            raise NxLibException(self.slot().path, NXLIB_EXECUTION_FAILED, self)
