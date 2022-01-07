from pymerger import AbstractAssembler
from pymerger import DataTypes
from re import match
from hashlib import sha256


class InvalidConverter(AbstractAssembler):
  
    def converter(self, path: str) -> str:
        return path

    def finder(self, keys: list) -> list:
        return [match(r'^_[a-f0-9]{64}_$', key) for key in keys]

    def handler(self, _: DataTypes, obj2: DataTypes) -> DataTypes:
        return obj2


class InvalidFinder(AbstractAssembler):

    def converter(self, data: DataTypes, path: str) -> str:
        return '_' + sha256(f'{data}+{path}'.encode('UTF-8')).hexdigest() + '_'

    def finder(self, keys: list, path: str) -> tuple:
        return keys, path

    def handler(self, _: DataTypes, obj2: DataTypes) -> DataTypes:
        return obj2


class InvalidHandler(AbstractAssembler):

    def converter(self, data: DataTypes, path: str) -> str:
        return '_' + sha256(f'{data}+{path}'.encode('UTF-8')).hexdigest() + '_'

    def finder(self, keys: list) -> list:
        return [match(r'^_[a-f0-9]{64}_$', key) for key in keys]

    def handler(self) -> None:
        pass


class NonImplementedAssembler(AbstractAssembler):
    pass
