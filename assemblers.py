from types import FunctionType
from abc import ABC
from abc import abstractmethod
from hashlib import sha256
from re import match

from errors import AssemblerImplementationError
from datatypes import DataTypes

class AbstractAssembler(ABC):
    '''doc'''

    def __init__(self) -> None:
        super().__init__()
        self._validate_methods_args(self.converter, 3)
        self._validate_methods_args(self.finder, 2)
        self._validate_methods_args(self.handler, 3)

    def _validate_methods_args(self, method: FunctionType, args_count) -> None:
        current_args_count = method.__code__.co_argcount
        if current_args_count != args_count:
            raise AssemblerImplementationError(
                f"Arguments count of {str(method).split(' ')[1]}"
                + f" must be {args_count} not {current_args_count}")


    @abstractmethod
    def converter(self, data: DataTypes, path: str) -> str:
        pass

    @abstractmethod
    def finder(self, keys: list) -> list:
        pass

    @abstractmethod
    def handler(self, obj1: DataTypes, obj2: DataTypes) -> DataTypes:
        pass


class DefaultAssembler(AbstractAssembler):
    '''doc'''

    def converter(self, data: DataTypes, path: str) -> str:
        return '_' + sha256(f'{data}+{path}'.encode('UTF-8')).hexdigest() + '_'

    def finder(self, keys: list) -> bool:
        return all(match(r'^_[a-f0-9]{64}_$', key) for key in keys)

    def handler(self, obj1: DataTypes, obj2: DataTypes) -> DataTypes:
        if obj2:
            return obj2
        return obj1


class UniqueRegexpAssembler(DefaultAssembler):
    '''doc'''

    def __init__(self, keys_paths_dict: dict) -> None:
        self._keys_paths_dict: dict[str, str] = keys_paths_dict
        super().__init__()

    def _get_unique_key_by_regexp_path(self, path: str) -> str | None:
        for path_regexp, unique_key in self._keys_paths_dict.items():
            if match(path_regexp, path):
                return unique_key

    def converter(self, data: DataTypes, path: str) -> str:
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
