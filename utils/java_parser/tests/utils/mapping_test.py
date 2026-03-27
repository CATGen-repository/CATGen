import os
import unittest

from Config import PROJECT_BASE
from utils import files
from utils.mappers import type_mapper
from utils.parsers import parse_class_declaration


class MappingTest(unittest.TestCase):
    def test_mapping_funcs(self):
        # load java class
        found_files = files.traverse_files(os.path.join(PROJECT_BASE, 'data'), required_postfix='.java')
        parsed_classes = []
        for file in found_files:
            file_content = files.read_file_with_UTF8(file)
            parsed_classes.extend(parse_class_declaration(file_content))
        type_mapper(parsed_classes)
        print(123)
