'''doc'''
from types import FunctionType
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

__default_assembler = DefaultAssembler()


def _get_converted_data(
        data: DataTypes,
        path: str = '/',
        converter: FunctionType = __default_assembler.converter) -> ConvertedDataTypes:
    converted_data: ConvertedDataTypes = {}
    if isinstance(data, dict):
        for key in data.keys():
            converted_data.update(
                {key: _get_converted_data(data[key], f'{path}{key}/', converter)})
    elif isinstance(data, list):
        for i, item in enumerate(data):
            converted_data.update(
                {
                    converter(item, f'{path}_{i}_/'):
                    _get_converted_data(item, f'{path}_{i}_/', converter)
                }
            )
    else:
        converted_data = data
    return converted_data


def _get_regular_data(
        data: ConvertedDataTypes,
        path: str = '/',
        finder: FunctionType = __default_assembler.finder) -> DataTypes:
    deconverted_data: DataTypes = {}
    if isinstance(data, dict):
        if finder(data.keys()):
            deconverted_data = []
            for key in data.keys():
                deconverted_data.append(
                    _get_regular_data(data[key], f'{path}{key}/', finder=finder))
        else:
            for key in data.keys():
                deconverted_data.update(
                    {key: _get_regular_data(data[key], f'{path}{key}/', finder=finder)})
    else:
        deconverted_data = data
    return deconverted_data


def _merge_converted_data(
        obj1: ConvertedDataTypes,
        obj2: ConvertedDataTypes,
        handler: FunctionType = __default_assembler.handler) -> ConvertedDataTypes:
    merged_converted_data: ConvertedDataTypes = {}
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        merged_converted_data = obj1.copy()
        obj1_keys = obj1.keys()
        obj2_keys = obj2.keys()
        for key in obj2_keys:
            if key in obj1_keys:
                merged_converted_data.update(
                    {key: _merge_converted_data(obj1[key], obj2[key], handler=handler)})
            else:
                merged_converted_data.update({key: obj2[key]})
    else:
        merged_converted_data = handler(obj1, obj2)
    return merged_converted_data


def merge_data(
        *objs: DataTypes,
        assembler: AbstractAssembler = __default_assembler) -> DataTypes:
    '''doc'''
    if len(objs) < 2:
        raise AttributesError(
            f'Merge only two and more objects (length of objs - {len(objs)})')
    merge_types: set = set(type(obj) for obj in objs if obj)
    if len(merge_types) > 1:
        merge_types_str: str = ', '.join(str(merge_type) for merge_type in merge_types)
        raise TypeError(f'All objects of merge must be a same type. Found {merge_types_str}')
    merged_data: ConvertedDataTypes = _get_converted_data(
        objs[0], converter=assembler.converter)
    for obj in objs[1:]:
        merged_data = _merge_converted_data(
            merged_data,
            _get_converted_data(obj, converter=assembler.converter),
            handler=assembler.handler)
    return _get_regular_data(merged_data, finder=assembler.finder)


def _validate_args(args: Namespace) -> None:
    no_exists_files: list = [file for file in args.files if not file_exists(file)]
    if no_exists_files:
        raise FileNotFoundError(f"File(s) '{', '.join(list(no_exists_files))}' not found!")
    dirs: list = [file for file in args.files if isdir(file)]
    if dirs:
        raise IsADirectoryError(f"A directories no supported ({', '.join(dirs)})")
    if file_exists(args.output):
        raise FileExistsError(f"File(s) '{args.output}' already exists")


def main():
    '''doc'''
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
    objects: list = []
    for file in args.files:
        with open(file, 'rt', encoding='UTF-8') as file_fd:
            objects.append(yaml_safe_load(file_fd.read()))
    merged: DataTypes = merge_data(*objects)
    with open(args.output, 'wt', encoding='UTF-8') as output_fd:
        if args.format == 'json':
            output_fd.write(json_dump(merged, sort_keys=False, indent=args.indent))
        else:
            output_fd.write(yaml_safe_dump(merged, sort_keys=False, indent=args.indent))


if __name__ == '__main__':
    main()
