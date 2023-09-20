# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# from test.mod_generics_cache import A  # type: ignore
import os
import sys
import django
import commonmark

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../.."))
os.environ["DJANGO_SETTINGS_MODULE"] = "odevlib_example.settings"
django.setup()


project = "ODevLib"
copyright = "2023, O.dev, https://the-o.co"
author = "O.dev"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    # Automatic generation of documentation from the Python code
    "autoapi.extension",
    # Theme setup
    "sphinx_rtd_theme",
    "sphinx_rtd_dark_mode",
    # Used to parse markdown files
    "myst_parser",
]

autoapi_type = "python"
autoapi_dirs = ["../odevlib"]
autoapi_add_toctree_entry = False

templates_path = ["_templates"]
exclude_patterns: list[str] = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_theme_options = {
    'navigation_depth': -1,
    'titles_only': True,
}


# Custom processor for docstrings that converts markdown to rst for sphinx to render.
# def docstring(app, what, name, obj, options, lines):
#     wrapped = []
#     literal = False
#     literal_indent = 0
#     for line in lines:
#         if line.strip().startswith(r"```"):
#             literal = not literal
#             literal_indent = len(line) - len(line.lstrip())
#             wrapped.append("\n")
#             continue
#         # if not literal:
#             # line = " ".join(x.rstrip() for x in line.split("\n"))
#             # line = " ".join(x.rstrip() for x in line.split("\n"))
#         if literal:
#             indent = len(line) - len(line.lstrip())
#             wrapped.append("\n" + " " * (indent - literal_indent) + line.strip())
#         # elif indent and not literal:
#             # wrapped.append(" " + line.lstrip())
#         else:
#             wrapped.append("\n" + line)
#     ast = commonmark.Parser().parse("".join(wrapped))
#     rst = commonmark.ReStructuredTextRenderer().render(ast)
#     lines.clear()
#     lines += rst.splitlines()


# Attach processor to the docstring processing hook
# def setup(app):
# app.connect("autodoc-process-docstring", docstring)
