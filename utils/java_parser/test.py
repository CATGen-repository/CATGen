import json
import os
import subprocess
from pathlib import Path

from loguru import logger
import pickle

from utils.entry import ContextParser
from tqdm import tqdm

if __name__ == "__main__":
    logger.info(f'Start Parse Project.')
    parser = ContextParser()
    parser.parse('/Users/wangziqi/Documents/projects/jfreechart')
    logger.info(f'Project parsed successfully.')

