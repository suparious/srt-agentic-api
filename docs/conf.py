import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'SRT Agentic API'
copyright = '2024, SolidRusT Networks'
author = 'Shaun Prince'
version = '0.1'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'
pygments_style = 'sphinx'
