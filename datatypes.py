"""The pymerger datatypes.

The module contains the types of data that the
Pymerger woks with.

Attributes:
    DataTypes (Union): The datatypes of a YAML/JSON-like object.
    ConvertedDataTypes (Union): The datatypes of a YAML/JSON-like object
        without the lists (arrays).
"""
from typing import Union
from types import NoneType

DataTypes = Union[dict, list, str, int, float, bool, NoneType]

ConvertedDataTypes = Union[dict, str, int, float, bool, NoneType]
