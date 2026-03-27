import sys
import pickle
from tree_sitter import Language, Parser
import tree_sitter_java as tsjava

JAVA_LANGUAGE = Language(tsjava.language(), name='java')
parser = Parser()
parser.language = JAVA_LANGUAGE
sys.path.extend([".", ".."])


def parse_fields_from_class_code(class_str: str):
    """
    Analyze defined fields for given class.
    :param class_str: class code in a string.
    :return: list of field dicts, for eaxmple:
            {
                "field_name": field_name,
                "field_type": field_type,
                "field_modifiers": field_modifiers,
                "declaration_text": declaration_text,
            }
    """
    root_node = parser.parse(bytes(class_str, "utf-8")).root_node
    rets = []

    field_decl_query = JAVA_LANGUAGE.query(
        """
        (field_declaration 
        (modifiers)@modifiers
            type: (_) @type_name 
            declarator: (variable_declarator name: (identifier)@var_name)
        ) @field_decl
        """
    )

    fields = field_decl_query.captures(root_node)
    num_iter = len(fields['field_decl']) if 'field_decl' in fields else 0
    for i in range(int(num_iter)):
        field_name = fields['var_name'][i].text.decode()
        field_type = fields['type_name'][i].text.decode()
        field_modifiers = fields['modifiers'][i].text.decode()
        declaration_text = fields['field_decl'][i].text.decode()
        if (field_name != "" and field_modifiers != "" and field_type != "" and declaration_text != ""):
            rets.append(
                {
                    "field_name": field_name,
                    "field_type": field_type,
                    "field_modifiers": field_modifiers,
                    "declaration_text": declaration_text,
                }
            )
    
    return rets


def parse_methods_from_class_node(class_str: str, need_prefix=False):
    """
    Analyze methods defined in the class.
    :param class_str:
    :return: list of collected methods. The elements are like:
                    {
                        "method_name": method_name,
                        "method_modifiers": method_modifiers,
                        "method_return_type": method_return_type,
                        "method_body": method_body,
                        "method_text": method_text,
                        "method_start_line": method start line,
                        "method_end_line": method end line
                    }
    """
    tmp_class_str = pickle.loads(pickle.dumps(class_str))
    root_node = parser.parse(bytes(tmp_class_str, "utf-8")).root_node
    rets = []

    method_query = JAVA_LANGUAGE.query(
        """
        (method_declaration) @method_decl
        """
    )
    method_attr_query = JAVA_LANGUAGE.query(
        """
        (method_declaration [
            (modifiers) @modifier
            type:(_) @ret_type
            name:(identifier) @name
            body:(block) @body
            ])
        """
    )
    comment_query = JAVA_LANGUAGE.query(
        """
        (line_comment) @lc
        (block_comment) @bc
        """
    )
    
    comments_results = comment_query.captures(root_node)
    comments = comments_results.get('lc', []) + comments_results.get('bc', [])
    comment_text_and_node = []
    comment_text = ""
    for index, comment_node in enumerate(comments):
        if index < len(comments) - 1 and comment_node.next_named_sibling == comments[index + 1]:
            comment_text = comment_text + '\n' + str(comment_node.text, encoding="utf-8")
        else:
            comment_text = comment_text + '\n' +str(comment_node.text, encoding="utf-8")
            comment_text_and_node.append((comment_node, comment_text))
            comment_text = ""
        
    methods = method_query.captures(root_node).get('method_decl', [])
    unique_methods = set()
    for index, method_node in enumerate(methods):
        method_comment = ''
        for comment_node, comment_text in comment_text_and_node:
            if comment_node.next_named_sibling == method_node:
                method_comment = comment_text
                break
        
        attrs = method_attr_query.captures(method_node)
        method_text = str(method_node.text, encoding="utf-8")
        method_return_type = str(attrs['ret_type'][0].text, encoding="utf-8")
        method_name = str(attrs['name'][0].text, encoding="utf-8")
        method_modifiers = str(attrs['modifier'][0].text, encoding="utf-8")
        method_body = str(attrs['body'][0].text, encoding="utf-8")
        method_start = method_node.start_point[0]
        method_end = method_node.end_point[0]

        if method_body not in unique_methods and method_body.strip() != "":
            unique_methods.add(method_body)
            rets.append(
                {
                    "method_name": method_name,
                    "method_modifiers": method_modifiers,
                    "method_return_type": method_return_type,
                    "method_body": method_body,
                    "method_text": method_comment + '\n' + method_text,
                    "method_start_line": method_start,
                    "method_end_line": method_end,
                    "method_comment": method_comment
                }
            )
    
    return rets


def parse_import_stmts_from_file_code(file_code: str):
    """
    从给定的代码文件内容中提取import。为了避免噪音，需要满足两个条件：
    1. import语句必须是分号结尾
    2. import语句至多含有三个以空格区分的token

    Args:
        file_code (str): 输入的代码文件内容（最好是代码文件，其他文件中可能会被过滤掉）

    Returns:
        list: 从输入内容中提取出的import strings
    """
    rets = []
    tree = parser.parse(bytes(file_code, "utf-8"))
    
    import_decl_query = JAVA_LANGUAGE.query("""(import_declaration) @import_decl""")
    imports = import_decl_query.captures(tree.root_node).get('import_decl', [])
    for import_stmt in imports:
        import_stmt = str(import_stmt.text, encoding="utf-8")
        tks = import_stmt.split()
        if import_stmt.endswith(";") and (len(tks) == 2 or len(tks) == 3):
            rets.append(import_stmt)
    return rets