import os
from loguru import logger

from utils import files
from utils.interface_parser import parse_interface_declaration
from utils.mappers import type_mapper
from utils.parsers import parse_class_declaration


class ContextParser:

    def __init__(self):
        self.parsed_classes = []
        pass

    def parse(self, project_base):
        # 判断是否存在文件夹
        if not os.path.exists(project_base):
            logger.error(f'Project base not found: {project_base}')
            return
        found_files = files.traverse_files(project_base, required_postfix='.java')
        logger.info(f'Found {len(found_files)} java files')
        for file in found_files:
            file_content = files.read_file_with_UTF8(file)
            self.parsed_classes.extend(parse_class_declaration(file_content, file))
            self.parsed_classes.extend(parse_interface_declaration(file_content, file))
        logger.info(f'Parsed {len(self.parsed_classes)} classes')
        type_mapper(self.parsed_classes)
        logger.info('Type mapping done')
