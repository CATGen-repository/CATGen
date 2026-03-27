import sys

sys.path.extend(['.', '..'])
from Config import *
from loguru import logger
from utils.files import read_file_with_UTF8, traverse_files
from utils.parsers import parse_methods, has_one_class, parse_class_declaration


def extract_methods(test_file):
    """
    This function is used to extract methods from a given test class file.

    Parameters:
    test_class_file (str): The path to the test class file.

    Returns:
    list: A list of methods if the file contains only one class.
          If the file contains multiple classes, an error is logged and an empty list is returned.
    """
    content = read_file_with_UTF8(test_file)
    cls_objs = parse_class_declaration(content)
    methods = []
    for cls_obj in cls_objs:
        if cls_obj.is_abstract:
            logger.info(f"Abstract class {cls_obj.name}.")
            continue
        cur_methods = parse_methods(cls_obj.text)
        for m in cur_methods:
            m._belongs = cls_obj.signature
            methods.append(m)
    logger.info(f"Found {len(methods)} methods in {test_file}")
    return methods




if __name__ == '__main__':
    for proj, path_mapping in CONFIG['path_mappings'].items():
        base_dir = path_mapping['loc']
        src_dir = os.path.join(base_dir, path_mapping['src'])
        files = traverse_files(src_dir, required_postfix='.java')
        for file in files:
            file_content = read_file_with_UTF8(file)
            methods = extract_methods(file)
        test_dir = os.path.join(base_dir, path_mapping['test'])
        files = traverse_files(test_dir, required_postfix='.java')
        for file in files:
            file_content = read_file_with_UTF8(file)
            uts = extract_methods(file)
    pass
