from types import FunctionType
from abc import ABC
from abc import abstractmethod
from hashlib import sha256
from re import match

from errors import AssemblerImplementationError
from datatypes import DataTypes

class AbstractAssembler(ABC):

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

    def converter(self, data: DataTypes, path: str) -> str:
        return '_' + sha256(f'{data}+{path}'.encode('UTF-8')).hexdigest() + '_'

    def finder(self, keys: list) -> bool:
        return all(match(r'^_[a-f0-9]{64}_$', key) for key in keys)

    def handler(self, obj1: DataTypes, obj2: DataTypes) -> DataTypes:
        if obj2:
            return obj2
        return obj1
