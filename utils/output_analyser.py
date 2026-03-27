import os
import pickle
import sys
import javalang
import javalang.tree
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava
import hashlib

JAVA_LANGUAGE = Language(tsjava.language(), name='java')
parser = Parser()
parser.language = JAVA_LANGUAGE

sys.path.extend(['.', '..'])

from .java_parser import (
    parse_import_stmts_from_file_code,
    parse_methods_from_class_node,
    parse_fields_from_class_code,
)

junit_imports = [
    # "import org.junit.Test;",
    # "import org.junit.Assert;",
    # "import org.junit.Before;",
    # "import org.junit.After;",
    # "import static org.junit.Assert.*;",
    # "import org.junit.Ignore;",
    # "import org.junit.BeforeClass;",
    # "import org.junit.AfterClass;",
    # "import org.junit.runner.RunWith;",
    # "import org.junit.runners.JUnit4;",
    # "import org.junit.Rule;",
    # "import org.junit.rules.ExpectedException;",
]

focal_imports = [
    # "import static org.mockito.Mockito.*;",
    # "import org.mockito.Mockito;",
    "import java.text.SimpleDateFormat;",
    "import java.io.*;",
    "import java.lang.*;",
    "import java.util.*;",
    "import java.time.*;",
    "import java.math.*;",
    "import java.sql.SQLException;",
    "import java.net.*;",
    "import java.security.*;",
    "import java.nio.file.Files;",
    "import java.nio.file.Path;",
    "import java.sql.*;",
]


def extract_elements_from_llm_generation(generation: str):
    """
    从LLM的输出结果中分析代码元素，组成测试类
    Args:
        generation: LLM的输出内容
    Returns:
        dict:{
                "msg": 提取结果，"success", "no llm output" 或 "no methods in output"
                "methods":[method],
                "imports":[import],
                "fields":[field],
                "uts": [ut],
            }
    """
    # 当LLM有正确输出的时候才进行下一步
    msg = "no llm output"
    imports, fields, methods, uts, set_up_methods = [], [], [], [], []
    if generation != "":
        methods, imports, fields = analyze_outputs(generation)
        set_up_methods = [
            method for method in methods if not '@Test' in method]
        uts = [method for method in methods if '@Test' in method]

        remove_uts = []
        for set_up_method in set_up_methods:
            method_name = get_method_name(set_up_method)
            if 'test' in method_name.lower():
                new_ut = set_up_method
                uts.append(new_ut)
                remove_uts.append(set_up_method)
            elif 'assert' in set_up_method:
                new_ut = set_up_method
                uts.append(new_ut)
                remove_uts.append(set_up_method)

        set_up_methods = [method for method in set_up_methods if method not in remove_uts]
        msg = "success"

    # 如果没有提取到任何method
    if len(uts) == 0:
        set_up_methods, imports, fields = [], [], []
        msg = "no methods in output"
        uts = []
    
    return {
        "msg": msg,
        "methods": set_up_methods,
        "uts": uts,
        "imports": imports,
        "fields": fields,
    }

def get_method_name_node(node):
    if node.type == 'method_declaration':
        return node.child_by_field_name('name')
    for child in node.children:
        name_node = get_method_name_node(child)
        if name_node is not None:
            return name_node
    return None

def get_method_name(code):
    '''提取method的名字'''
    tree = parser.parse(bytes(code, "utf8"))
    root = tree.root_node
    return get_method_name_node(root).text.decode()

def analyze_outputs(output_str: str):
    block_dot_lines = []
    lines = output_str.split("\n")
    for line_id, line in enumerate(lines):
        if line.startswith("```"):
            block_dot_lines.append(line_id)
    total_lines = len(lines)
    methods = []
    imports = []
    fields = []
    start = 0
    for line_id in block_dot_lines:
        if line_id == 0:
            start = 1
            continue
        cur_block = lines[start: line_id]
        cur_content = "\n".join(cur_block)
        if lines[line_id].startswith("```"):
            pass
        else:
            column_id = lines[line_id].find("```")
            if column_id == -1:
                raise IndexError(
                    f"Failing in finding ``` starters in {lines[line_id]}")
            else:
                cur_content += lines[line_id][:column_id]

        methods.extend([i["method_text"] for i in parse_methods_from_class_node(cur_content)])
        imports.extend(parse_import_stmts_from_file_code(cur_content))
        fields.extend([i["declaration_text"] for i in parse_fields_from_class_code(cur_content)])
        start = line_id + 1
        pass

    if start < total_lines:
        if start == 0:
            pass
        else:
            start += 1
        cur_block = lines[start:]
        cur_content = "\n".join(cur_block)
        cur_methods = parse_methods_from_class_node(cur_content)
        if len(cur_methods) != 0:
            methods.extend([i["method_text"] for i in parse_methods_from_class_node(cur_content)])
            imports.extend(parse_import_stmts_from_file_code(cur_content))
            fields.extend([i["declaration_text"] for i in parse_fields_from_class_code(cur_content)])
    imports = list(set(imports))
    methods = list(set(methods))
    fields = list(set(fields))
    
    return methods, imports, fields

def remove_whitespace(s):
    # 使用 str 的 replace 方法去除常见的空白字符
    for whitespace in [' ', '\t', '\n', '\r']:
        s = s.replace(whitespace, '')
    return s

def update_fields(fields):
    new_fields = []
    cleaned_fields = []
    for field in fields:
        try:
            cleaned_field = remove_whitespace(field)
            if cleaned_field in cleaned_fields:
                continue
            cleaned_fields.append(cleaned_field)
            new_fields.append(field)
        except:
            continue

    return new_fields

def update_imports(imports):
    new_imports = []
    cleaned_imports = []
    for imp in imports:
        try:
            cleaned_import = remove_whitespace(imp)
            if cleaned_import in cleaned_imports:
                continue
            cleaned_imports.append(cleaned_import)
            new_imports.append(imp)
        except:
            continue

    return new_imports

def extract_method_name(method_code):
    # Parse the Java code
    method_code = "public class TmpClass {\n" + method_code + "}\n"
    tree = javalang.parse.parse(method_code)

    method_names = []
    for _, node in tree.filter(javalang.tree.MethodDeclaration):
        method_names.append(node.name)
    return method_names[0]

def update_setup_methods(setup_methods):
    current_method_names = {}
    new_methods = []
    cleaned_methods = []
    for method in setup_methods:
        try:
            cleaned_method = remove_whitespace(method)
            if cleaned_method in cleaned_methods:
                continue
            cleaned_methods.append(cleaned_method)
            method_name = extract_method_name(method)
            if method_name in current_method_names.keys():
                current_method_names[method_name] = (current_method_names[method_name] + 1)
                method = method.replace(method_name, method_name + str(current_method_names[method_name]))
            else:
                current_method_names[method_name] = 0
                method = method.replace(method_name, method_name + str(current_method_names[method_name]))
            new_methods.append(method)
        except:
            continue

    return new_methods

def get_all_infos_from_llm_output(test_class_content, llm_output):
    imports, fields, setup_methods, uts = [], [], [], []
    if isinstance(llm_output, str):
        test_classes = [llm_output]
    elif isinstance(llm_output, list):
        test_classes = llm_output
    
    for test_class in test_classes:
        single_result = extract_elements_from_llm_generation(test_class)
        if single_result["msg"] == "success":
            imports.extend(single_result["imports"])
            fields.extend(single_result["fields"])
            setup_methods.extend(single_result["methods"])
            uts.extend(single_result["uts"])
    
    imports = [imp for imp in imports if remove_whitespace(imp) not in remove_whitespace(test_class_content)]
    imports = update_imports(imports)
    
    # 提取出来的fields和setup_methods，需要去除掉已经存在的
    fields = [field for field in fields if remove_whitespace(field) not in remove_whitespace(test_class_content)]
    fields = update_fields(fields)
    setup_methods = [method for method in setup_methods if remove_whitespace(method) not in remove_whitespace(test_class_content)]
    setup_methods = update_setup_methods(setup_methods)
    
    return {
        "imports": imports,
        "fields": fields,
        "setup_methods": setup_methods,
        "uts": uts,
    }

def assemble_test_class_content(test_class_content, llm_output_info, ut):
    imports, fields, setup_methods, uts = llm_output_info["imports"], llm_output_info["fields"], llm_output_info["setup_methods"],  llm_output_info["uts"]
    
    class_decl_query = JAVA_LANGUAGE.query('(class_declaration)@class_declaration')
    field_query = JAVA_LANGUAGE.query('(class_declaration body:(_(field_declaration)@field_declaration))')
    method_query = JAVA_LANGUAGE.query('(class_declaration body:(_(method_declaration)@method_declaration))')
    field_query = JAVA_LANGUAGE.query('(class_declaration body:(_(field_declaration)@field_declaration))')
    import_query = JAVA_LANGUAGE.query('(import_declaration)@import')
    field_name_query = JAVA_LANGUAGE.query('(variable_declarator name: (identifier)@field_name)')
    
    root_node = parser.parse(bytes(test_class_content, "utf8")).root_node
    class_declaration_nodes  = class_decl_query.captures(root_node).get('class_declaration', None)
    if not class_declaration_nodes:
        raise Exception('No class declaration node found in the test class content')
    else:
        class_declaration_node = class_declaration_nodes[0]
    method_nodes = method_query.captures(class_declaration_node).get('method_declaration', [])
    field_nodes = field_query.captures(class_declaration_node).get('field_declaration', [])
    import_nodes = import_query.captures(root_node).get('import', [])
    
    add_list = []
    
    add_import = ''
    for imp in imports:
        add_import += imp + '\n'
    if len(import_nodes) > 0:
        add_list.append((import_nodes[-1].end_byte, add_import))
    
    already_field_name = {}
    for filed_node in field_nodes:
        field_name = field_name_query.captures(filed_node)['field_name'][0].text.decode()
        already_field_name[field_name] = True
    add_field = ''
    for field in fields:
        field_name = field_name_query.captures(parser.parse(bytes(field, "utf8")).root_node)['field_name'][0].text.decode()
        if field_name in already_field_name:
            continue
        add_field += '    ' + field + '\n'
    if len(field_nodes) > 0:
        add_list.append((field_nodes[-1].end_byte, add_field))
    
    add_method = ''
    for method in setup_methods:
        add_method += method + '\n'
    add_method += ut + '\n'
    if len(method_nodes) > 0:
        add_list.append((method_nodes[-1].end_byte, add_method))
    
    new_test_class_content = ''.encode('utf8')
    test_class_content = test_class_content.encode('utf8')
    start_byte = 0
    for add_location, add_text in add_list:
        new_test_class_content += test_class_content[start_byte:add_location] + '\n'.encode() + add_text.encode('utf8')
        start_byte = add_location
    new_test_class_content += test_class_content[start_byte:]
    return new_test_class_content.decode('utf8')


'''
后面几个函数是静态处理大模型输出结果
'''
def calculate_md5(data):
    """计算给定数据的MD5哈希值"""
    md5 = hashlib.md5()
    md5.update(data.encode("utf-8"))
    return md5.hexdigest()


def extract_test_class_without_imports(response_msg):
    lines = response_msg.split('\n')
    in_block = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('```'):
            if in_block:
                in_block = False
                continue
            else:
                in_block = True
                continue
        if in_block and not line.startswith('import'):
            new_lines.append(line)
    return '\n'.join(new_lines)


def extract_code_block_with_imports(response_msg):
    lines = response_msg.split('\n')
    in_block = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('```'):
            if in_block:
                in_block = False
                continue
            else:
                in_block = True
                continue
        if in_block:
            new_lines.append(line)
    return '\n'.join(new_lines)




if __name__ == '__main__':
    test_class_content = '''
@MockitoSettings(strictness = Strictness.LENIENT)
class HomeControllerTest {
    @Mock(answer = Answers.RETURNS_DEEP_STUBS)
    private HomeService homeService;

    @InjectMocks
    private HomeController homeController;

    private AutoCloseable mockitoCloseable;

    @BeforeEach
    void setUp() throws Exception {
        mockitoCloseable = MockitoAnnotations.openMocks(this);
    }

    @AfterEach
    void tearDown() throws Exception {
        mockitoCloseable.close();
    }
}
    '''
    llm_output = '''
    package org.jfree.data.general;
// from focal class
// from src
// from LLM
// pre-defined
import org.jfree.data.pie.PieDataset;

public class LLMGeneratedTests {
private XYDataset dataset;
private Function2D function2D;
private CategoryDataset categoryDataset;
private PieDataset pieDataset;
private TableXYDataset tableXYDataset;
//123
@After
    public void tearDown() {
        dataset = null;
        categoryDataset = null;
        pieDataset = null;
        tableXYDataset = null;
        function2D = null;
    }


@Before
    public void setUp() {
        dataset = mock(XYDataset.class);
        categoryDataset = mock(CategoryDataset.class);
        pieDataset = mock(PieDataset.class);
        tableXYDataset = mock(TableXYDataset.class);
        function2D = mock(Function2D.class);
    }
    @Test
    public void testIterateRangeBoundsWithEmptyDataset() {
        when(dataset.getSeriesCount()).thenReturn(0);
        Range result = DatasetUtilities.iterateRangeBounds(dataset);
        assertNull(result);
    }
}
    '''
    llm_info = get_all_infos_from_llm_output(test_class_content, llm_output)
    new_test_class_content = assemble_test_class_content(test_class_content, llm_info, '')
    a = 1
