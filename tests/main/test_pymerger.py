# VERY UGLY !!!

from unittest import TestCase
from unittest import main
from unittest import skip
from os.path import join
from os import remove
from subprocess import run as run_process
from subprocess import CompletedProcess

from yaml import safe_load as yaml_safe_load

from test_classes import InvalidConverter
from test_classes import InvalidFinder
from test_classes import InvalidHandler
from test_classes import NonImplementedAssembler
from datatypes import DataTypes
from pymerger import merge_data
from errors import AttributesError
from errors import AssemblerImplementationError


class TestMerge(TestCase):

    def _test_merge_data(self, *yaml_files_paths: list, yaml_merged: str):
        yaml_data_list: list = []
        for yaml_file in yaml_files_paths:
            with open(yaml_file, 'rt', encoding='UTF-8') as yaml_file_desc:
                yaml_data_list.append(yaml_safe_load(yaml_file_desc.read()))
        with open(yaml_merged, 'rt', encoding='UTF-8') as yd_merged:
            yaml_data_merged = yaml_safe_load(yd_merged.read())
        yaml_data_merged_result: DataTypes = merge_data(*yaml_data_list)
        if isinstance(yaml_data_merged_result, dict):
            self.assertDictEqual(yaml_data_merged_result, yaml_data_merged)
        if isinstance(yaml_data_merged_result, list):
            self.assertListEqual(yaml_data_merged_result, yaml_data_merged)
        else:
            self.assertEqual(yaml_data_merged_result, yaml_data_merged)

    def test_merge_all_empty_objects(self) -> None:
        self._test_merge_data(
            join('tests', 'main', 'res', 'all_empty', 'test_0.yml'),
            join('tests', 'main', 'res', 'all_empty', 'test_1.yml'),
            yaml_merged = join('tests', 'main', 'res', 'all_empty', 'test_merged.yml')
        )

    def test_merge_with_one_empty(self) -> None:
        self._test_merge_data(
            join('tests', 'main', 'res', 'one_empty', 'test_0.yml'),
            join('tests', 'main', 'res', 'one_empty', 'test_1.yml'),
            yaml_merged = join('tests', 'main', 'res', 'one_empty', 'test_merged.yml')
        )

    def test_merge_with_one_empty_reverse(self) -> None:
        self._test_merge_data(
            join('tests', 'main', 'res', 'one_empty', 'test_0.yml'),
            join('tests', 'main', 'res', 'one_empty', 'test_1.yml'),
            yaml_merged = join('tests', 'main', 'res', 'one_empty', 'test_merged.yml')
        )

    def test_merge_dicts(self) -> None:
        self._test_merge_data(
            join('tests', 'main', 'res', 'dicts', 'test_0.yml'),
            join('tests', 'main', 'res', 'dicts', 'test_1.yml'),
            yaml_merged = join('tests', 'main', 'res', 'dicts', 'test_merged.yml')
        )

    def test_merge_lists(self) -> None:
        self._test_merge_data(
            join('tests', 'main', 'res', 'lists', 'test_0.yml'),
            join('tests', 'main', 'res', 'lists', 'test_1.yml'),
            yaml_merged = join('tests', 'main', 'res', 'lists', 'test_merged.yml')
        )

    def test_merge_same_objects(self) -> None:
        self._test_merge_data(
            join('tests', 'main', 'res', 'same', 'test_0.yml'),
            join('tests', 'main', 'res', 'same', 'test_1.yml'),
            yaml_merged = join('tests', 'main', 'res', 'same', 'test_merged.yml')
        )

    def test_merge_complex_objects(self) -> None:
        self._test_merge_data(
            join('tests', 'main', 'res', 'complex', 'test_0.yml'),
            join('tests', 'main', 'res', 'complex', 'test_1.yml'),
            yaml_merged = join('tests', 'main', 'res', 'complex', 'test_merged.yml')
        )

    def test_multi_merge_complex_objects(self) -> None:
        self._test_merge_data(
            join('tests', 'main', 'res', 'multi_complex', 'test_0.yml'),
            join('tests', 'main', 'res', 'multi_complex', 'test_1.yml'),
            join('tests', 'main', 'res', 'multi_complex', 'test_2.yml'),
            yaml_merged = join('tests', 'main', 'res', 'multi_complex', 'test_merged.yml')
        )

    def test_merge_passing_incorrect_attrs(self) -> None:
        with self.assertRaises(AttributesError):
            merge_data({})

    def test_merge_different_objects_types(self) -> None:
        test_data: tuple = (
            ({'foo': 'bar'}, 'some string'),
            ('some string', ['foo', 'bar']),
            ({'foo': 'bar'}, ['foo', 'bar']),
        )
        for item1, item2 in (test_data):
            with self.assertRaises(TypeError):
                merge_data(item1, item2)


class TestImplementation(TestCase):

    def test_invalid_converter(self) -> None:
        with self.assertRaises(AssemblerImplementationError):
            InvalidConverter()

    def test_invalid_finder(self) -> None:
        with self.assertRaises(AssemblerImplementationError):
            InvalidFinder()

    def test_invalid_handler(self) -> None:
        with self.assertRaises(AssemblerImplementationError):
            InvalidHandler()

    def test_non_implemented_assembler(self) -> None:
        with self.assertRaises(TypeError):
            NonImplementedAssembler()


class TestModuleRun(TestMerge):

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName=methodName)
        self.python_interpreter_path = join('pyvenv', 'Scripts', 'python')

    def _test_merge_data(self, *yaml_files_paths: list, yaml_merged: str):
        yaml_result_file_path = join('tests', 'main', 'tmp_result.yml')
        try:
            res = run_process(
                [self.python_interpreter_path, 'pymerger.py',
                 *yaml_files_paths, '--output', yaml_result_file_path
                ],
                text=True, check=False, capture_output=True)
            print(res.stderr)
            with open(yaml_merged, 'rt', encoding='UTF-8') as yaml_merged_desc:
                yaml_merged_str = yaml_merged_desc.read().strip().lstrip('---').rstrip('...')
            with open(yaml_result_file_path, 'rt', encoding='UTF-8') as yaml_result_desc:
                yaml_result_str = yaml_result_desc.read().strip().lstrip('---').rstrip('...')
            self.assertEqual(yaml_merged_str, yaml_result_str)
        finally:
            remove(yaml_result_file_path)
    
    def test_non_existent_file(self) -> None:
        test_file_1: str = join('tests', 'main', 'res', 'complex', 'test_0.yml')
        test_file_2: str = join('tests', 'main', 'res', 'non-existent-file.yml')
        result: CompletedProcess = run_process(
            [self.python_interpreter_path, 'pymerger.py', test_file_1, test_file_2],
            text=True, capture_output=True)
        self.assertTrue('FileNotFoundError' in result.stderr)
        self.assertTrue(test_file_2 in result.stderr)
        self.assertFalse( test_file_1 in result.stderr)

    def test_directory_file(self) -> None:
        test_file_1: str = join('tests', 'main', 'res', 'complex', 'test_0.yml')
        test_file_2: str = join('tests', 'main', 'res', 'complex')
        result: CompletedProcess = run_process(
            [self.python_interpreter_path, 'pymerger.py', test_file_1, test_file_2],
            text=True, capture_output=True)
        self.assertTrue('IsADirectoryError' in result.stderr)
        self.assertTrue(test_file_2 in result.stderr)
        self.assertFalse(test_file_1 in result.stderr)

    def test_result_file_already_exists(self) -> None:
        test_file_1: str = join('tests', 'main', 'res', 'complex', 'test_0.yml')
        test_file_2: str = join('tests', 'main', 'res', 'complex', 'test_1.yml')
        test_file_3: str = join('tests', 'main', 'res', 'complex', 'test_merged.yml')
        result: CompletedProcess = run_process(
            [self.python_interpreter_path, 'pymerger.py',
             test_file_1, test_file_2,'--output', test_file_3
            ],
            text=True, capture_output=True)
        self.assertTrue('FileExistsError' in result.stderr)
        self.assertTrue(test_file_3 in result.stderr)
        self.assertFalse(test_file_1 in result.stderr)
        self.assertFalse(test_file_2 in result.stderr)

    @skip('Already ran in TestMerge')
    def test_merge_passing_incorrect_attrs(self) -> None:
        pass

    @skip('Already ran in TestMerge')
    def test_merge_different_objects_types(self) -> None:
        pass


if __name__ == '__main__':
    main()
