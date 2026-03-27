import sys

sys.path.extend(['.', '..'])
import unittest

from utils.ut_extractor import *


class TestUTExtractor(unittest.TestCase):
    def test_extract_uts_should_raise_exception_when_test_class_file_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            extract_uts('')


if __name__ == '__main__':
    unittest.main()
