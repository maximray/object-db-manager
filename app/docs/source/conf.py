# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('../../../'))  # Путь к корню проекта

extensions = [
    'sphinx.ext.autodoc',      # Для automodule, autoclass и др.
    'sphinx.ext.viewcode',     # Просмотр исходного кода
    'sphinx.ext.napoleon',     # Поддержка Google/Numpy стиля
    'sphinx.ext.coverage',     # Проверка покрытия документации
    'sphinx.ext.autosummary'   # Авто-суммаризация
]

# Включите поддержку специальных членов
autodoc_default_options = {
    'members': True,
    'special-members': '__init__',
    'undoc-members': True,
    'show-inheritance': True
}

html_theme = 'sphinx_rtd_theme'

project = 'course'
copyright = '2025, Maxim Raykov'
author = 'Maxim Raykov'
release = '1'

templates_path = ['_templates']
exclude_patterns = []

language = 'ru'


html_theme = 'alabaster'
html_static_path = ['_static']
