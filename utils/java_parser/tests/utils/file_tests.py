import os.path
import sys

sys.path.extend(['.', '..'])

from Config import PROJECT_BASE
import unittest
from utils import files


class TestFiles(unittest.TestCase):

    def test_traverse_files_with_existing_directory(self):
        found_files = files.traverse_files(os.path.join(PROJECT_BASE, 'entities'))
        after_remove_pycache = []
        for file in found_files:
            if '__pycache__' in file:
                continue
            after_remove_pycache.append(file)
        self.assertEqual(len(after_remove_pycache), 4)
        self.assertTrue(os.path.normpath(os.path.join(PROJECT_BASE, 'entities/Class.py')) in found_files)
        self.assertTrue(os.path.normpath(os.path.join(PROJECT_BASE, 'entities/Method.py')) in found_files)
        self.assertTrue(os.path.normpath(os.path.join(PROJECT_BASE, 'entities/Project.py')) in found_files)
        self.assertTrue(os.path.normpath(os.path.join(PROJECT_BASE, 'entities/Variable.py')) in found_files)

    def test_traverse_files_with_non_existing_directory(self):
        with self.assertRaises(FileNotFoundError):
            files.traverse_files('/non_existing_path')

    def test_read_file_with_utf8_encoding(self):
        self.assertEqual(files.read_file_with_UTF8(os.path.join(PROJECT_BASE, 'tests/test_source/test_read_file.txt')),
                         'testOneTwoThree')

    def test_read_file_with_non_utf8_encoding(self):
        self.assertEqual(
            files.read_file_with_UTF8(os.path.join(PROJECT_BASE, 'tests/test_source/test_read_file_iso8859_1.txt')),
            'testOneTwoThree')

    # def test_read_file_with_unknown_encoding(self):
    #     with self.assertRaises(UnicodeEncodeError):
    #         files.read_file_with_UTF8(os.path.join(PROJECT_BASE,'tests/test_source/test_read_file_utf-16.txt'))

    def test_read_file_with_non_existing_file(self):
        with self.assertRaises(FileNotFoundError):
            files.read_file_with_UTF8('/non_existing_path/file')


if __name__ == '__main__':
    unittest.main()
