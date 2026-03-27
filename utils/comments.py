from tree_sitter import Language, Parser
import tree_sitter_java as tsjava

JAVA_LANGUAGE = Language(tsjava.language(), name='java')
parser = Parser()
parser.language = JAVA_LANGUAGE


def remove_comments(source_code: str) -> str:
    """
    Remove comments from the source code.
    :param source_code: The source code as a string.
    :return: The source code without comments.
    """
    tree = parser.parse(bytes(source_code, 'utf8'))
    root_node = tree.root_node

    comment_query = parser.language.query("""
        (block_comment) @comment
        (line_comment) @comment
        """)

    comment_nodes = comment_query.captures(root_node).get('comment', [])
    
    # 需要删掉的列表,用空字符串替代
    replace_list = []
    for comment_node in comment_nodes:
        replace_list.append((comment_node.start_byte, comment_node.end_byte, ''))

    return replace_text_by_byte_positions(source_code, replace_list)


def replace_text_by_byte_positions(content, replacements):
    """
    根据字节位置替换文本内容。
    
    Args:
        content (str): 原始文本内容
        replacements (list): 替换规则列表 [[start_pos, end_pos, replacement_text], ...]
    
    Returns:
        str: 替换后的文本内容
    """
    if not replacements:
        return content
    
    byte_content = content.encode('utf-8')
    sorted_replacements = sorted(replacements, key=lambda x: x[0])
    
    # 构建结果片段列表
    result_parts = []
    last_end_pos = 0
    
    for start_pos, end_pos, replacement_text in sorted_replacements:
        # 添加原始内容片段
        result_parts.append(byte_content[last_end_pos:start_pos])
        # 添加替换内容
        result_parts.append(replacement_text.encode('utf-8'))
        last_end_pos = end_pos
    
    # 添加最后的原始内容
    result_parts.append(byte_content[last_end_pos:])
    
    # 合并所有片段并解码
    return b''.join(result_parts).decode('utf-8')
