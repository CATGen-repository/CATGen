import os
import sys

sys.path.extend(['.', '..'])

import pickle
# from Config import CONFIG
from utils.files import traverse_files, read_file_with_UTF8


def map_uts_and_source_methods(src_methods, existing_uts):
    """
    This function is used to map source methods to existing unit tests.

    Parameters:
    src_methods (list): A list of methods extracted from the source code.
    existing_uts (list): A list of methods extracted from the existing unit tests.

    Returns:
    dict: A dictionary where the key is the method name and the value is a tuple of the method and the unit test.
    """
    method_map = {}
    for src_method in src_methods:
        belonged_cls_sig = src_method.belongs
        print(belonged_cls_sig)
    return method_map


def type_mapper(classes):
    for cls in classes:
        cls.replace_import_types(classes)
    for cls in classes:
        cls.method_call_mapping(classes)


def method_call_mapper(classes, mi, method_signatures):
    # 首先找到名字一样的函数们
    # 然后对比参数列表
    if classes is None:
        return None
    methods = [m for m in classes._class_methods if m.name == mi.name]
    for m in methods:
        flag = True
        if len(m.params) != len(method_signatures):
            continue
        for i in range(len(m.params)):
            if m.params[i].type != method_signatures[i]:
                flag = False
                break
        if flag:
            mi._belongs_to = m
            break


if __name__ == '__main__':
    pass
    # source_methods = []
    # test_methods = []
    #
    # src_method_save_path = CONFIG['all_method_save_path']
    # ut_save_path = CONFIG['all_ut_save_path']
    #
    # if os.path.exists(src_method_save_path) and os.path.exists(ut_save_path):
    #     with open(src_method_save_path, 'rb') as f:
    #         source_methods = pickle.load(f)
    #     with open(ut_save_path, 'rb') as f:
    #         test_methods = pickle.load(f)
    #     pass
    # else:
    #     for proj, path_mapping in CONFIG['path_mappings'].items():
    #         base_dir = path_mapping['loc']
    #         src_dir = os.path.join(base_dir, path_mapping['src'])
    #         files = traverse_files(src_dir, required_postfix='.java')
    #         for file in files:
    #             file_content = read_file_with_UTF8(file)
    #             source_methods.extend(extract_methods(file))
    #         test_dir = os.path.join(base_dir, path_mapping['test'])
    #         files = traverse_files(test_dir, required_postfix='.java')
    #         for file in files:
    #             file_content = read_file_with_UTF8(file)
    #             test_methods.extend(extract_methods(file))
    #     with open(src_method_save_path, 'wb') as f:
    #         pickle.dump(source_methods, f)
    #     with open(ut_save_path, 'wb') as f:
    #         pickle.dump(test_methods, f)
    #
    # map_uts_and_source_methods(source_methods, test_methods)
    # pass
