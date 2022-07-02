"""The assemblers for a conflict resolution.

The module contains the standard assemblers.
During the merge process, conflicts can occur,
such as merging arrays or data other than a dictionary.
Assemblers are used to resolve these conflicts.
"""
from types import FunctionType
from abc import ABC
from abc import abstractmethod
from hashlib import sha256
from re import match

from errors import AssemblerImplementationError
from datatypes import DataTypes

class AbstractAssembler(ABC):
    """The abstract class of the assemblers.

    The conversion lists to dictionaries.
    During the recursive conversion process, every the arrays in the data
    objects converts to the dictionaries using the 'converter' function.
    This function is passed the arguments of the array element
    and its path relative to the data object. The function then returns
    the key generated based on the passed arguments.

    Finding a converted lists.
    After converting and merging arrays, you need to find the converted arrays
    and bring them to their regular form. To do this, used the
    'finder' function. This function is passed the keys list of every
    objects in the data objects and if the objects is the converted array
    then it returns True otherwise False.

    Handling of the type conflicts.
    During the recursive merge process if the types of first
    and seconds objects not equal the dict, then both objects
    pass to the 'handler' function, which returns the result of the merge.

    For example, see the DefaultAssembler docs.
    """

    def __init__(self) -> None:
        super().__init__()
        self._validate_methods_args(self.converter, 3)
        self._validate_methods_args(self.finder, 2)
        self._validate_methods_args(self.handler, 3)

    def _validate_methods_args(self, method: FunctionType, args_count: int) -> None:
        """Validation on the methods implementation.

        The Lite validation of the passed arguments to the implemented methods
        of the AbstractAssembler class.
        Raise error if the count of the method arguments not equal
        to the expected count.

        Args:
            method: the implemented method (converter, finder or handler).
            args_count: The count of the method arguments.

        Return:
            None.

        Raises:
            AssemblerImplementationError: An error ocurred if the count
                of the arguments not equal to the expected count.
        """
        current_args_count = method.__code__.co_argcount
        if current_args_count != args_count:
            raise AssemblerImplementationError(
                f"Arguments count of {str(method).split(' ')[1]}"
                + f" must be {args_count} not {current_args_count}")

    @abstractmethod
    def converter(self, data: DataTypes, path: str) -> str:
        """Generate and return the key based on the object and it path.

        Args:
            data: The data object (DataTypes).
            path: The relative path of the data object.

        Returns:
            The generated key.
        """

    @abstractmethod
    def finder(self, keys: list) -> bool:
        """Find the converted arrays.

        Find the converted arrays. Return True if keys at a object
        corresponds the converted data object keys.

        Args:
            keys: The list of keys.

        Returns:
            True if keys at a object corresponds the converted
            data object keys else False.
        """

    @abstractmethod
    def handler(self, obj1: DataTypes, obj2: DataTypes) -> DataTypes:
        """Get the merge result.

        Get the result of the two objects merge.

        Args:
            obj1: The first data object (DataTypes).
            obj2: The second data object (DataTypes).

        Return:
            The merged data object (DataTypes).
        """


class DefaultAssembler(AbstractAssembler):
    """The default assembler class.

    The simple implementation of the AbstractAssembler class.
    """

    def converter(self, data: DataTypes, path: str) -> str:
        """Generate and return the key based on the object and it path.

        The return key is a SHA-256 hash-based string
        with underscores added to the beginning and end.
        It always matches the pattern /^_[a-f0-9]{64}_$/.

        Args:
            data: The data object (DataTypes).
            path: The relative path of the data object

        Returns:
            The generated key.
        """
        return '_' + sha256(f'{data}+{path}'.encode('UTF-8')).hexdigest() + '_'

    def finder(self, keys: list) -> bool:
        """Find the converted arrays.

        Check if every key matches the pattern /^_[a-f0-9]{64}_$/.

        Args:
            keys: The list of keys.

        Returns:
            True if keys at a object corresponds the converted
            data object keys else False.
        """
        return all(match(r'^_[a-f0-9]{64}_$', key) for key in keys)

    def handler(self, obj1: DataTypes, obj2: DataTypes) -> DataTypes:
        """Get the merge result.

        If the second data object is exists and not empty
        the result of the merge is the second data object
        else is the first data object.

        Args:
            obj1: The first data object (DataTypes).
            obj2: The second data object (DataTypes).

        Return:
            The merged data object (DataTypes).
        """
        if obj2:
            return obj2
        return obj1


class UniqueRegexpAssembler(DefaultAssembler):
    """Uniqueization of array elements by key.

    Sometimes a more complex conversion of arrays to dictionaries
    is needed than described above (in DefaultAssembler).
    This class is inherited from the DefaultAssembler
    with a override of the 'converter' method and new attribute (_keys_paths_dict).

    The conversion is not based on the relative path of the object
    and its content, but based on the value of a key that is unique
    to that element.

    For example, if
    ::

        obj1 = {
            'users': [
                {
                    'user_id': 123,
                    'name': 'Alex'
                }
            ]
        }
        obj2 = {
            'users': [
                {
                    'user_id': 123,
                    'surname': 'Morgan'
                }
            ]
        }
        assembler = UniqueRegexpAssembler({'\\/users\\/.+': 'user_id'})
    then
    ::

        merge_data(obj1, obj2, assembler=assembler)

    returns the
    ::

        {
            'users': [
                {
                    'user_id': 123,
                    'name': 'Alex',
                    'surname': 'Morgan'
                }
            ]
        }

    Note:
        if change assembler to
        ::

            assembler = DefaultAssembler()
        then
        ::

            merge_data(obj1, obj2, assembler=assembler)
        returns the
        ::

            {
                'users': [
                    {
                        'user_id': 123,
                        'name': 'Alex'
                    },
                    {
                        'user_id': 123,
                        'surname': 'Morgan'
                    }
                ]
            }

    Attributes:
        _keys_paths_dict: dict of the regex: unique element key
    """

    def __init__(self, keys_paths_dict: dict) -> None:
        self._keys_paths_dict: dict[str, str] = keys_paths_dict
        super().__init__()

    def _get_unique_key_by_regexp_path(self, path: str) -> str | None:
        """Get unique key by regexp path.
        """
        for path_regexp, unique_key in self._keys_paths_dict.items():
            if match(path_regexp, path):
                return unique_key

    def converter(self, data: DataTypes, path: str) -> str:
        """Generate and return the key.

        Generate and return the key based on the unique value
        of the object and its relative path in a data object.

        Args:
            data: The data object (DataTypes).
            path: The relative path of the data object.

        Returns:
            The generated key.
        """
        hex_hash: str
        base_list_path = '/'.join(path.split('/')[0:-2]) + '/'
        key_by_path: str = self._get_unique_key_by_regexp_path(path)
        if key_by_path:
            try:
                unique_value = data[key_by_path]
                hex_hash = '_' + sha256(
                    f'{unique_value}+{base_list_path}'.encode('UTF-8')
                    ).hexdigest() + '_'
            except (TypeError, KeyError):
                hex_hash = super().converter(data, path)
        else:
            hex_hash = super().converter(data, path)
        return hex_hash
