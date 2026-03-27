import os
import json
import sys
import random
import string

from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava

JAVA_LANGUAGE = Language(tsjava.language(), name='java')
parser = Parser()
parser.language = JAVA_LANGUAGE


def generate_random_string(length):
    characters = string.ascii_letters + string.digits  # 包含大写字母、小写字母和数字
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def take_methods(class_content):
    root_node = parser.parse(bytes(class_content, "utf-8")).root_node
    method_query = JAVA_LANGUAGE.query('(method_declaration)@method_decl')
    method_name_query = JAVA_LANGUAGE.query('(method_declaration name:(identifier)@class_name)')
    
    method_list = []
    for method_node in method_query.captures(root_node).get('method_decl', []):
        method_name_node = method_name_query.captures(method_node).get('class_name', [None])[0]
        if method_name_node:
            method_name = method_name_node.text.decode()
            method_list.append((method_name, method_node.text.decode()))
        else:
            print("No method name found for method node:", method_node.text.decode())
    
    return method_list


    
def remove_duplicate_method_names(class_list):
    method_name_set = set()
    new_class_list = []
    for class_content in class_list:
        method_list = take_methods(class_content)
        new_class_content = class_content
        for method_name, method_content in method_list:
            if method_name == 'setUp' or method_name == 'tearDown':
                continue
            if method_name not in method_name_set:
                method_name_set.add(method_name)
            else:
                print(f'发现了重名的: {method_name}')
                new_method_name = f'{method_name}_{generate_random_string(8)}'
                new_method_content = method_content.replace(method_name, new_method_name)
                new_class_content = new_class_content.replace(method_content, new_method_content)
                method_name_set.add(new_method_name)
        new_class_list.append(new_class_content)
    
    return new_class_list


def process_jsonl(jsonl_path):
    with open(jsonl_path, 'r', encoding='utf-8') as file:
        contexts = [json.loads(line) for line in file.readlines()]

    # 处理completion
    class_list = []
    for context in contexts:
        if 'completion' in context:
            class_list.append(context['completion'])

    class_list = remove_duplicate_method_names(class_list)
    
    for context, class_content in zip(contexts, class_list):
        if 'completion' in context:
            context['completion'] = class_content
    
    # 处理fixed_completion
    class_list = []
    for context in contexts:
        if 'fixed_completion' in context:
            class_list.append(context['fixed_completion'])

    class_list = remove_duplicate_method_names(class_list)
    
    for context, class_content in zip(contexts, class_list):
        if 'fixed_completion' in context:
            context['fixed_completion'] = class_content

    # 保存结果
    with open(jsonl_path, 'w') as jsonl_file:
        for item in contexts:
            jsonl_file.write(json.dumps(item, ensure_ascii=False) + '\n')



