from jinja2 import Environment, FileSystemLoader, select_autoescape

import sys

from pathlib import Path
import sys
import os

root_path = str(Path(Path(__file__).parent.absolute()).parent.absolute().parent.absolute())
structure_path = os.path.join(root_path, 'structure')
html_path = os.path.join(structure_path, 'html')
templates_path = os.path.join(html_path, 'templates')
sys.path.append(templates_path)

jinja2_env = Environment(
    loader=FileSystemLoader(templates_path),
)
