from unittest import TestCase
from unittest import main
from os.path import join

from yaml import safe_load as yaml_safe_load

from pymerger import merge_data
from datatypes import DataTypes
from assemblers import AbstractAssembler
from assemblers import UniqueRegexpAssembler

class TestAssemblers(TestCase):

    def _test_assembler(
            self, 
            file_path_1: str, 
            file_path_2: str, 
            file_path_merged: str,
            assembler: AbstractAssembler) -> None:
        with open(file_path_1, 'rt', encoding='UTF-8') as yaml_file_fd:
            yaml_data_1: DataTypes = yaml_safe_load(yaml_file_fd.read())
        with open(file_path_2, 'rt', encoding='UTF-8') as yaml_file_fd:
            yaml_data_2: DataTypes = yaml_safe_load(yaml_file_fd.read())
        with open(file_path_merged, 'rt', encoding='UTF-8') as yaml_file_fd:
            yaml_data_merged: DataTypes = yaml_safe_load(yaml_file_fd.read())
        yaml_data_merged_result = merge_data(
            yaml_data_1, yaml_data_2, assembler=assembler)
        self.assertDictEqual(yaml_data_merged, yaml_data_merged_result)

    def test_unique_key_by_path_assembler(self) -> None:
        yaml_file_path_1: str = join(
            'tests', 'assemblers', 'res', 'unique_key_by_path', 'test_0.yml')
        yaml_file_path_2: str = join(
            'tests', 'assemblers', 'res', 'unique_key_by_path', 'test_1.yml')
        yaml_file_result_path: str = join(
            'tests', 'assemblers', 'res', 'unique_key_by_path', 'test_merged.yml')
        self._test_assembler(
            yaml_file_path_1, 
            yaml_file_path_2, 
            yaml_file_result_path, 
            UniqueRegexpAssembler({r'\/users\/.+': 'user_id'}))


if __name__ == '__main__':
    main()
