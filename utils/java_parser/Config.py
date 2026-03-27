import os
import sys
import json
from tree_sitter import Language
import tree_sitter_java as tsjava
from Exceptions import *

sys.path.extend(['.', '..'])

PROJECT_BASE = os.path.dirname(__file__)
_config_file = os.path.join(PROJECT_BASE, 'config.json')

# if not os.path.exists(_config_file):
#     print(f'ERROR: Config file {_config_file} does not exist, please check')

# with open(_config_file, 'r', encoding='utf-8') as f:
#     CONFIG = json.loads(f.read())

JAVA_LANGUAGE = Language(tsjava.language(), name='java')

KNOWN_ASSERTIONS = [
    'assertEquals',
    'assertTrue',
    'assertFalse',
    'assertNull',
    'assertNotNull',
    'assertThat',
    'assertArrayEquals',
    'assertNotEquals',
    'assertThrows',
    'assertSame',
    'assertNotSame',
    'fail',
]
