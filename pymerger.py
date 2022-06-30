"""Merge the YAML/JSON-like objects or files.

The module allows you to merge several YAML/JSON-like objects
(or files) into one.
You can use it in your project or standalone.
The module contains an extensible conflict resolution logic
such as merging objects of different types or merging arrays.
(See "assembler" module documentation.)

WARNING! In all examples of the module was used the DefaultAssembler

Examples:

    # Use the pymerger in your project
    from pymerger import merge_data
    o1 = {
        'a': 1,
        'b': 'qwe',
        'c': [1, 2, 3]
    }
    o2 = {
        'a': 2,
        'd': 3
    }
    o3 = {
        'e': 4,
        'c': [4, 5]
    }
    print(merge_data(o1, o2, o3))
    # {
    #   'a': 2,
    #   'b': 'qwe',
    #   'c': [1, 2, 3, 4, 5],
    #   'd': 3,
    #   'e': 4
    # }
    # CAUTION! The result may depend on the assembler you choose
    # Default assembler is the DefaultAssembler

    # Use pymerger standalone
    python -m pymerger file1.yml file2.yml -o result.yml
    # result.yml result of merge file1.yml and file2.yml
    # In this mode will use the DefaultAssembler
"""
from argparse import ArgumentParser
from argparse import Namespace
from json import dumps as json_dump
from os.path import exists as file_exists
from os.path import isdir

from yaml import safe_load as yaml_safe_load
from yaml import safe_dump as yaml_safe_dump

from errors import AttributesError
from assemblers import AbstractAssembler
from assemblers import DefaultAssembler
from datatypes import DataTypes
from datatypes import ConvertedDataTypes


def _get_converted_data(
        data: DataTypes,
        path: str,
        assembler: AbstractAssembler) -> ConvertedDataTypes:
    """Get the converted data of the object.

    Get the object, in which all arrays are converted to dictionaries.

    Args:
        data: A dict object to be converted (DataTypes).
        path: A current item path (from data) (String).
        assembler: A assembler for arrays to dictionaries conversion
            (AbstractAssembler).

    Returns:
        A dict object (ConvertedDataTypes), in which all arrays
        are converted to the dictionaries.
        For example:
        if
            data = ['list item 1', 'list item 2', 'list item 3']
        then
            converted_data = {
                'generated_key_1': 'list item 1',
                'generated_key_2': 'list item 2',
                'generated_key_3': 'list item 3',
            }
    """
    converted_data = {}
    if isinstance(data, dict):
        for key in data.keys():
            converted_data.update(
                {key: _get_converted_data(data[key], f'{path}{key}/', assembler)})
    elif isinstance(data, list):
        for i, item in enumerate(data):
            converted_data.update(
                {
                    assembler.converter(item, f'{path}_{i}_/'):
                    _get_converted_data(item, f'{path}_{i}_/', assembler)
                }
            )
    else:
        converted_data = data
    return converted_data


def _get_regular_data(
        data: ConvertedDataTypes,
        assembler: AbstractAssembler) -> DataTypes:
    """Get a regular data of object.

    Get a normalized data object from the converted data object
    (The reverse function of _get_converted_data).

    Args:
        data: A dict object to be converted (ConvertedDataTypes).
        assembler: A assembler to find arrays that have been converted to objects
            (AbstractAssembler).

    Returns:
        A normalized dict object (DataTypes).
        For example:
        if
            data = {
                'generated_key_1': 'list item 1',
                'generated_key_2': 'list item 2',
                'generated_key_3': 'list item 3',
            }
        then
            normalized_data = ['list item 1', 'list item 2', 'list item 3']
    """
    regular_data = {}
    if isinstance(data, dict):
        if assembler.finder(data.keys()):
            regular_data = []
            for key in data.keys():
                regular_data.append(
                    _get_regular_data(data[key], assembler))
        else:
            for key in data.keys():
                regular_data.update(
                    {key: _get_regular_data(data[key], assembler)})
    else:
        regular_data = data
    return regular_data


def _merge_converted_data(
        obj1: ConvertedDataTypes,
        obj2: ConvertedDataTypes,
        assembler: AbstractAssembler) -> ConvertedDataTypes:
    """Merge a converted data objects into one object.

    Recursive merge two converted data objects into one object.

    Args:
        obj1: A first converted data object (ConvertedDataTypes).
        obj2: A second converted data object (ConvertedDataTypes).
        assembler: A assembler for conflict types resolution.
            If the obj1 and the obj2 has no type dict, then assembler.handler
            must be handle the conflict.

    Returns:
        A result of merge two converted data objects.
        For example:
        if
            obj1 = {
                'qwe': '123',
                'lol': {
                    'generated_key_1': 'item_1',
                    'generated_key_2': 'item_2'
                }
            }
            obj2 = {
                'asd': '456',
                'lol': {
                    'generated_key_3': 'item_3'
                }
            }
        then
            converted_obj = {
                'qwe': '123',
                'asd': '456',
                'lol': {
                    'generated_key_1': 'item_1',
                    'generated_key_2': 'item_2',
                    'generated_key_3': 'item_3'
                }
            }
    """
    merged_converted_data: ConvertedDataTypes = {}
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        merged_converted_data = obj1.copy()
        obj1_keys = obj1.keys()
        obj2_keys = obj2.keys()
        for key in obj2_keys:
            if key in obj1_keys:
                merged_converted_data.update(
                    {key: _merge_converted_data(obj1[key], obj2[key], assembler)})
            else:
                merged_converted_data.update({key: obj2[key]})
    else:
        merged_converted_data = assembler.handler(obj1, obj2)
    return merged_converted_data


def merge_data(
        *objs: DataTypes,
        assembler: AbstractAssembler = DefaultAssembler()) -> DataTypes:
    """Merge the data objects into one data object.

    Recursive merge several data objects into one data object.
    All the objects must be a same type.

    Args:
        objs: A list of data objects to merge (DataTypes).
        assembler: A special instance of the AbstractAssembler for
            realization extensible merge logic
            (such as merging objects of different types or merging arrays).
            A default assembler is instance of the DefaultAssembler.
            In all examples was used the DefaultAssembler.

    Returns:
        A result of merge several data objects.
        For example:
        if
            o1 = {
                'a': 1,
                'b': 'qwe',
                'c': [1, 2, 3]
            }
            o2 = {
                'a': 2,
                'd': 3
            }
            o3 = {
                'e': 4,
                'c': [4, 5]
            }
        then teh result will be
            {
                'a': 2,
                'b': 'qwe',
                'c': [1, 2, 3, 4, 5],
                'd': 3,
                'e': 4
            }

    Raises:
        AttributesError: If count of the objects lower the two
        TypeError: If the objects of different types
    """
    if len(objs) < 2:
        raise AttributesError(
            f'Merge only two and more objects (length of objs - {len(objs)})')
    merge_types = set(type(obj) for obj in objs if obj)
    if len(merge_types) > 1:
        merge_types_str = ', '.join(str(merge_type) for merge_type in merge_types)
        raise TypeError(f'All objects of merge must be a same type. Found {merge_types_str}')
    merged_data = _get_converted_data(objs[0], '/', assembler)
    for obj in objs[1:]:
        merged_data = _merge_converted_data(
            merged_data,
            _get_converted_data(obj, '/',assembler),
            assembler)
    return _get_regular_data(merged_data, assembler)


def _validate_args(args: Namespace) -> None:
    """Validate a received arguments.

    Validate a received arguments of ArgumentParser in standalone run.
    Check if the received files paths is exists.
    Check if the received files paths is not a directory.
    Check if the output file path is not exists.

    Args:
        args: The parsed arguments (Namespace).

    Returns:
        None.

    Raises:
        FileNotFoundError: If one or mode files paths is not exists.
        IsADirectoryError: If one or more files paths is a directory.
        FileExistsError: If an output file already exists.
    """
    files_statuses: list = [file for file in args.files if not file_exists(file)]
    if files_statuses:
        raise FileNotFoundError(f"File(s) '{', '.join(list(files_statuses))}' not found!")
    dirs: list = [file for file in args.files if isdir(file)]
    if dirs:
        raise IsADirectoryError(f"A directories no supported ({', '.join(dirs)})")
    if file_exists(args.output):
        raise FileExistsError(f"File(s) '{args.output}' already exists")


def main() -> int:
    """The main function.

    The main function of the pymerger standalone mode.
    Run 'python -m pymerger --help' for more info.

    Args:
        None.

    Returns:
        A status code of process.
    """
    argument_parser = ArgumentParser()
    argument_parser.add_argument('files', nargs='+', help='Paths to YAML/JSON with objects')
    argument_parser.add_argument(
        '--output', '-o',
        type=str,
        default='merged_result.yml',
        help='Path to output file (default: ./merged_result.yml)')
    argument_parser.add_argument(
        '--format', '-f',
        type=str,
        choices=['yaml', 'json'],
        default='yaml',
        help='Output file format: yaml or json (default: yaml)')
    argument_parser.add_argument(
        '--indent', '-i',
        type=int,
        default=None,
        help='Indent value for pretty-print result dumps (default: None)')
    args = argument_parser.parse_args()
    _validate_args(args)
    objects = []
    for file in args.files:
        with open(file, 'rt', encoding='UTF-8') as file_fd:
            objects.append(yaml_safe_load(file_fd.read()))
    merged_result: DataTypes = merge_data(*objects)
    with open(args.output, 'wt', encoding='UTF-8') as output_fd:
        if args.format == 'json':
            output_fd.write(json_dump(merged_result, sort_keys=False, indent=args.indent))
        else:
            output_fd.write(yaml_safe_dump(merged_result, sort_keys=False, indent=args.indent))


if __name__ == '__main__':
    main()
