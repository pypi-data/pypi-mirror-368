import json

import numpy as np

from nxlib import api
from nxlib.constants import *
from nxlib.exception import NxLibError, NxLibException


__all__ = ["NxLibItem"]


class NxLibItem:
    """
    This class simplifies the concatenation of string and integer constants to
    an NxLib compatible item path specification via its ``[]`` operator.
    Assignment (``=`` and ``<<``) and comparison operators (``<``,  ``<=``,
    ``==``,  ``!=``, ``>`` and ``>=``) simplify the usage of NxLib tree items,
    almost as if using local variables.

    Args:
        path (str, optional): The item's path. If None is given, the item will
            reference the root of the tree. Defaults to None.
    """
    def __init__(self, path=None):
        if path is None:
            path = ""
        self.path = path

    def __getitem__(self, value):
        path = self.path + NXLIB_ITEM_SEPARATOR
        if type(value) is str:
            return NxLibItem(path + value)
        elif type(value) is int:
            return NxLibItem(path + NXLIB_INDEX_ESCAPE_CHAR + str(value))
        else:
            raise NxLibError("Value cannot be added to NxLib path")

    def __setitem__(self, path, value):
        """
        The ``=`` operator. Set the item's value at the given path to the given
        value.

        Args:
            path (str): The path of the item to be set.
            value (int, str, bool or double): The value to be set.
        """
        self[path]._set_t(value)

    def _compare(self, value):
        item_value = self.value()
        if type(item_value) == type(value):
            if item_value == value:
                return 0
            elif item_value < value:
                return -1
            else:
                return 1
        else:
            raise NxLibException(self.path, NXLIB_ITEM_TYPE_NOT_COMPATIBLE)

    def __lt__(self, value):
        """
        The ``<`` comparison operator.

        Args:
            value (int, str, bool or double): The value to compare the item's
                value against.

        Returns:
            bool: True if item's value is less than given value, False
            otherwise.
        """
        return self._compare(value) < 0

    def __le__(self, value):
        """
        The ``<=`` comparison operator.

        Args:
            value (int, str, bool or double): The value to compare the item's
                value against.

        Returns:
            bool: True if item's value is less or eqaul to given value,
            False otherwise.
        """
        return self._compare(value) <= 0

    def __eq__(self, value):
        """
        The ``==`` comparison operator.

        Args:
            value (int, str, bool or double): The value to compare the item's
                value against.

        Returns:
            bool: True if item's value is eqaul to given value, False otherwise.
        """
        return self._compare(value) == 0

    def __ne__(self, value):
        """
        The ``!=`` comparison operator.

        Args:
            value (int, str, bool or double): The value to compare the item's
                value against.

        Returns:
            bool: True if item's value is not eqaul to given value, False
            otherwise.
        """
        return self._compare(value) != 0

    def __gt__(self, value):
        """
        The ``>`` comparison operator.

        Args:
            value (int, str, bool or double): The value to compare the item's
                value against.

        Returns:
            bool: True if item's value is greater than given value, False
            otherwise.
        """
        return self._compare(value) > 0

    def __ge__(self, value):
        """
        The ``>=`` comparison operator.

        Args:
            value (int, str, bool or double): The value to compare the item's
                value against.

        Returns:
            bool: True if item's value is greater or eqaul to given value,
            False otherwise.
        """
        return self._compare(value) >= 0

    def __lshift__(self, other):
        """
        The ``<<`` operator.

        Sets a new value for the item.

        Args:
            other (str, `NxLibItem` or any type that is convertible via `json.dumps()`):
                The new value to set the item's value to.

        Raises:
            NxLibException: If ``other`` is neither of the allowed types.
        """
        if type(other) is str:
            self.set_json(other, True)
        elif isinstance(other, NxLibItem):
            self.set_json(other.as_json(), True)
        else:
            try:
                self.set_json(json.dumps(other), True)
            except Exception as e:
                raise NxLibException(self.path, NXLIB_ITEM_TYPE_NOT_COMPATIBLE) from e

    def _set_t(self, value):
        if value is None:
            self.set_null()
        elif type(value) is int:
            if (value > 2147483647 or value < -2147483648):
                raise NotImplementedError()
            else:
                self.set_int(value)
        elif type(value) is str:
            self.set_string(value)
        elif type(value) is bool:
            self.set_bool(value)
        elif type(value) is float:
            self.set_double(value)
        else:
            raise NxLibException(self.path, NXLIB_ITEM_TYPE_NOT_COMPATIBLE)

    def set_null(self):
        """ Sets an item to the value Null. """
        api.set_null(self.path)

    def set_double(self, value):
        """
        Sets an item to the given double value.

        Args:
            value (double): Float value to be set.
        """
        api.set_double(self.path, value)

    def set_int(self, value):
        """
        Sets an item to the given int value.

        Args:
            value (int): Integer value to be set.
        """
        api.set_int(self.path, value)

    def set_bool(self, value):
        """
        Sets an item to the given boolean value.

        Args:
            value (bool): Boolean value to be set.
        """
        api.set_bool(self.path, value)

    def set_string(self, value):
        """
        Sets an item to the given string value.

        Args:
            value (string): String value to be set.
        """
        api.set_string(self.path, value)

    def set_json(self, value, only_writable_nodes=False):
        """
        Sets an item to the given JSON value. The value might itself be an
        entire tree structure which will be placed under the specified node.

        Args:
            value (JSON string): The JSON string representing the value or
                subtree to write.
            only_writable_nodes (bool, optional): Specifies whether the function
                should try to write each single node into the existing tree
                structure instead of replacing the entire subtree. When
                specifying True here the function will not complain if certain
                nodes could not be written due to access restrictions. This can
                be used to restore the state of the library or the Parameters
                node of a camera if the tree state has previously been captured
                via :meth:`~as_json`. When this parameter is set to false, all
                items of the entire subtree must not be access restricted in
                order for the function call to succeed! If this parameter is set
                and the given JSON value does not match the current structure of
                the node, the function will return the error code
                ``NxLibItemTypeNotCompatible``. This indicates, that there was
                not a single node with the same structure as in the JSON string
                and the function could never modify any value. In this case you
                probably tried to apply the JSON value to the wrong path.
                Defaults to False.
        """
        api.set_json(self.path, value, only_writable_nodes)

    def set_value(self, obj, only_writable_nodes=False):
        """
        Sets the value of the NxLibItem from a native Python object.

        Internally serializes the provided Python object to a JSON string using
        `json.dumps()`, then calls `set_json()` to update the item's content.

        This method allows setting the item's content generically from Python-native
        data structures such as dicts, lists, strings, numbers, booleans, or None.

        Args:
            obj (Any): A Python object representing the desired content of the item.
                Typically a dict, list, int, float, str, bool, or None.
            only_writable_nodes (bool, optional): Specifies whether the function
                should try to write each individual node into the existing tree
                structure instead of replacing the entire subtree. If set to True,
                the function will not raise errors for nodes that cannot be written
                due to access restrictions. This is useful for restoring a previously
                captured tree state when some nodes may be read-only. Defaults to False.

        Raises:
            NxLibException: If `set_json()` fails due to invalid JSON serialization,
                structure incompatibility, or if the underlying item rejects the data.

        Returns:
            None
        """
        json_str = json.dumps(obj)
        self.set_json(json_str, only_writable_nodes=only_writable_nodes)

    def set_binary_data(self, buffer, buffer_size_or_width=0, height=0,
                        channel_count=0, bytes_per_element=0, is_float=0):
        """
        Sets data of a ``Binary`` item with either an OpenCV matrix or another
        array object (e.g. Numpy array). In the first case, this function calls
        :meth:`~set_binary_data_from_cv`. In the second case it sets
        the data formatted if ``channel_count`` is non-zero and uses
        ``buffer_size_or_width`` as width, otherwise it sets the data
        unformatted and uses ``buffer_size_or_width`` as buffer size.

        Args:
            buffer (``Object``): Either a OpenCV matrix or another array object
                (e.g. a Numpy array).
            buffer_size_or_width (int, optional): Either the buffer size or the
                array width. Defaults to 0.
            height (int, optional): [description]. The array height to 0.
            channel_count (int): Number of channels for a single item.
                Defaults to 0.
            bytes_per_element (int, optional): Size in bytes of a single channel
                value of an item. Defaults to 0.
            is_float (int, optional): Specifies whether the element data type is
                a floating point type. Defaults to 0.
        """
        if buffer_size_or_width == 0:
            self.set_binary_data_from_cv(buffer)
        elif (channel_count > 0):
            width = buffer_size_or_width
            api.set_binary_formatted(self.path, buffer, width, height,
                                     channel_count, bytes_per_element,
                                     is_float)
        else:
            buffer_size = buffer_size_or_width
            api.set_binary(self.path, buffer, buffer_size)

    def set_binary_data_from_cv(self, mat):
        """
        Sets data of a ``Binary`` item with an OpenCV matrix.

        Args:
            mat (OpenCV matrix): The matrix containing the data to set the item
                content to.

        Raises:
            NxLibException: With NxLib Error ``NxLibItemTypeNotCompatible`` if
                ``mat`` is not an ``ndarray``.
        """
        if type(mat).__name__ != 'ndarray':
            raise NxLibException(self.path, NXLIB_ITEM_TYPE_NOT_COMPATIBLE)

        is_float = False
        if mat.dtype == 'uint8' or mat.dtype == 'int8':
            bytes_per_element = 1
        elif mat.dtype == 'uint16' or mat.dtype == 'int16':
            bytes_per_element = 2
        elif mat.dtype == 'int32':
            bytes_per_element = 4
        elif mat.dtype == 'float32':
            bytes_per_element = 4
            is_float = True
        elif mat.dtype == 'float64':
            bytes_per_element = 8
            is_float = True

        buffer = np.ctypeslib.as_ctypes(mat)
        height, width, channel_count = np.atleast_3d(mat).shape
        api.set_binary_formatted(self.path, buffer, width, height,
                                 channel_count, bytes_per_element, is_float)

    def get_binary_data(self):
        """
        Retrieves data of a ``Binary`` item.

        Returns:
            ``Object``: A byte buffer containing the binary data.
        """
        buffer, buffer_size = self._create_buffer()
        cbuffer = np.ctypeslib.as_ctypes(buffer)
        api.get_binary(self.path, cbuffer, buffer_size)
        return buffer

    def _create_buffer(self):
        binary_data_info = self.get_binary_data_info()
        bytes_per_element, is_float = binary_data_info[3], binary_data_info[4]
        nptype = np.uint8
        if is_float:
            if bytes_per_element == 4:
                nptype = np.float32
            elif bytes_per_element == 8:
                nptype = np.float64
        else:
            if bytes_per_element == 1:
                nptype = np.uint8
            elif bytes_per_element == 2:
                nptype = np.int16
            elif bytes_per_element == 4:
                nptype = np.int32
        width, height, channel_count = binary_data_info[:3]
        buffer = np.zeros((height, width, channel_count), nptype, order='C')
        buffer_size = width * height * channel_count * buffer.dtype.itemsize
        return buffer, buffer_size

    def get_binary_data_info(self):
        """
        Retrieves meta data of a ``Binary`` item.

        Returns:
            tuple containing

            * width (int): The width of the array (consecutive elements in
              memory).
            * height (int): The height of the array (number of rows of ``width``
              * ``channel_count`` elements)
            * channel_count (int): Number of channels for a single item.
            * bytes_per_element (int): Size in bytes of a single channel value
              of an item.
            * is_float (bool): Specifies whether the element data type is a
              floating point type.
            * timestamp (str): The current ``timestamp`` of the binary blob
              queried.
        """
        return api.get_binary_info(self.path)

    def value(self):
        """
        Returns the value of the NxLibItem as a native Python object.

        Internally calls `as_json()` to retrieve the serialized representation,
        and then deserializes it using `json.loads()` to produce the corresponding
        Python object.

        This is a convenient, generic method for extracting the item's content
        without explicitly checking for its type.

        Example:
            >>> item.value()
            {'SerialNumber': '12332672398', ...}

        Raises:
            NxLibException: If `as_json()` fails or the result is not valid JSON.

        Returns:
            Any: The Python representation of the item's content, e.g., dict, list, int, float, str, bool, or None.
        """
        return json.loads(self.as_json())

    def as_int(self):
        """
        Returns the item value as int.

        Raises:
            NxLibException: With NxLib Error ``NxLibItemTypeNotCompatible`` if
                item is not an int.

        Returns:
            int: The item value.
        """
        return api.get_int(self.path)

    def as_bool(self):
        """
        Returns the item value as bool.

        Raises:
            NxLibException: With NxLib Error ``NxLibItemTypeNotCompatible`` if
                item is not a bool.

        Returns:
            bool: The item value.
        """
        return api.get_bool(self.path)

    def as_double(self):
        """
        Returns the item value as double.

        Raises:
            NxLibException: With NxLib Error ``NxLibItemTypeNotCompatible`` if
                item is not a double.

        Returns:
            double: The item value.
        """
        return api.get_double(self.path)

    def as_string(self):
        """
        Returns the item value as string.

        Raises:
            NxLibException: With NxLib Error ``NxLibItemTypeNotCompatible`` if
                item is not a string.

        Returns:
            str: The item value.
        """
        return api.get_string(self.path)

    def count(self):
        """
        Retrieves the number of subitems of an ``Object`` or the number of
        elements of an ``item``. In case of a ``Binary`` item its data size in
        bytes is returned.

        Returns:
            int: The number of subitems.
        """
        return api.get_count(self.path)

    def as_json(self, pretty_print=1, number_precision=18,
                scientific_number_format=0):
        """
        Retrieves an item value or an entire subtree in JSON representation.

        Args:
            pretty_print (int, optional): Specifies whether to use pretty
                printing. Int is treated as bool. Defaults to 1.
            number_precision (int, optional): The floating point precision of
                the returned numbers. Defaults to 2.
            scientific_number_format (int, optional): Specifies whether to use
                scientific notation for all numbers. Int is treated as bool.
                Defaults to 0.

        Returns:
            JSON string: A JSON string representing the item value or subtree.
        """
        return api.get_json(self.path, pretty_print, number_precision,
                            scientific_number_format)

    def as_json_meta(self, num_levels=1, pretty_print=1, number_precision=18,
                     scientific_number_format=0):
        """
        Retrieves an item value or an entire subtree in JSON representation
        including item metadata (protection, extended type, internal flags).

        Args:
            num_levels (int, optional): The depth of the returned subtree. Nodes
                in lower levels will be omitted. Defaults to 1.
            pretty_print (int, optional): Specifies whether to use pretty
                printing. Int is treated as bool. Defaults to 1.
            number_precision (int, optional): The floating point precision of
                the returned numbers. Defaults to 2.
            scientific_number_format (int, optional): Specifies whether to use
                scientific notation for all numbers. Int is treated as bool.
                Defaults to 0.

        Returns:
            JSON string: A JSON string representing the item value or subtree
            including each item's metadata.
        """
        return api.get_json_meta(self.path, num_levels, pretty_print,
                                 number_precision, scientific_number_format)

    def type(self):
        """
        Retrieves the item type of a tree item.

        Returns:
            int: The type identifier of the basic type of the item.
            See :mod:`~api.constants` for constants named
            ``NXLIB_ITEM_TYPE_*``
        """
        return api.get_type(self.path)

    def is_null(self):
        """
        Returns:
            bool: True if item is null, False otherwise.
        """
        return self.type() == NXLIB_ITEM_TYPE_NULL

    def is_string(self):
        """
        Returns:
            bool: True if item is a string, False otherwise.
        """
        return self.type() == NXLIB_ITEM_TYPE_STRING

    def is_number(self):
        """
        Returns:
            bool: True if item is a number (int or double), False otherwise.
        """
        return self.type() == NXLIB_ITEM_TYPE_NUMBER

    def is_int(self):
        """
        Returns:
            bool: True if item is an integer, False otherwise.
        """
        return self.is_number() and self.as_double().is_integer()

    def is_double(self):
        """
        Returns:
            bool: True if item is a double, False otherwise.
        """
        return self.is_number() and not self.as_double().is_integer()

    def is_bool(self):
        """
        Returns:
            bool: True if item is a bool, False otherwise.
        """
        return self.type() == NXLIB_ITEM_TYPE_BOOL

    def is_array(self):
        """
        Returns:
            bool: True if item is an array, False otherwise.
        """
        return self.type() == NXLIB_ITEM_TYPE_ARRAY

    def is_object(self):
        """
        Returns:
            bool: True if item is an object, False otherwise.
        """
        return self.type() == NXLIB_ITEM_TYPE_OBJECT

    def exists(self):
        """
        Returns:
            bool: True if item exists, False otherwise.
        """
        return api.has_path(self.path)

    def name(self):
        """

        Returns:
            str: The item name.
        """
        return api.get_name(self.path)

    def erase(self):
        """ Erases the item from the tree. """
        api.erase(self.path)

    def wait_for_change(self):
        """
        Wait for any change of the item, i.e. a change of value or item type.
        """
        api.wait_for_change(self.path)

    def wait_for_type(self, awaited_type, wait_for_equal):
        """
        Wait for a type change of the item. When the condition to wait for is
        already satisfied initially, the function returns immediately.

        Args:
            awaited_type (item_type): The item type to wait for.
            wait_for_equal (bool): If True, the function waits until the
                item has the specified type, otherwise it waits until the item
                has a different type than the one specified.
        """
        api.wait_for_type(self.path, awaited_type, wait_for_equal)

    def wait_for_int_value(self, value, wait_for_equal):
        """
        Wait for specific integer value of the item. When the condition to wait
        for is already satisfied initially, the function returns immediately.

        Args:
            value (int): The value to wait for.
            wait_for_equal (bool): If True, the function waits until the item
                has the specified type, otherwise it waits until the item has a
                different type than the one specified.
        """
        api.wait_for_int_value(self.path, value, wait_for_equal)

    def wait_for_string_value(self, value, wait_for_equal):
        """
        Wait for specific string value of the item. When the condition to wait
        for is already satisfied initially, the function returns immediately.

        Args:
            value (str): The value to wait for.
            wait_for_equal (bool): If True, the function waits until the item
                has the specified type, otherwise it waits until the item has a
                different type than the one specified.
        """
        api.wait_for_string_value(self.path, value, wait_for_equal)

    def wait_for_bool_value(self, value, wait_for_equal):
        """
        Wait for specific boolean value of the item. When the condition to wait
        for is already satisfied initially, the function returns immediately.

        Args:
            value (bool): The value to wait for.
            wait_for_equal (bool): If True, the function waits until the item
                has the specified type, otherwise it waits until the item has a
                different type than the one specified.
        """
        api.wait_for_bool_value(self.path, value, wait_for_equal)

    def wait_for_double_value(self, value, wait_for_equal):
        """
        Wait for specific double value the item. When the condition to wait
        for is already satisfied initially, the function returns immediately.

        Args:
            value (double): The value to wait for.
            wait_for_equal (bool): If True, the function waits until the item
                has the specified type, otherwise it waits until the item has a
                different type than the one specified.
        """
        api.wait_for_double_value(self.path, value, wait_for_equal)

    def make_unique_item(self, item_name=None):
        """
        Creates a new item with a unique name.

        Args:
            item_name (str, optional): The parent path of the new item to
                create. Defaults to None.

        Returns:
            str: The name of the generated item.
        """
        new_path = api.make_unique_item(self.path, item_name)
        if new_path:
            return NxLibItem(new_path)
        return NxLibItem()
