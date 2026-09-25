import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "log_server"
author = "Kengo NAKADA"
language = "ja"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = [
    "deflist",
    "colon_fence",
    "linkify",
]

autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

autodoc_typehints = "description"
autodoc_preserve_defaults = True

# API documentation can be generated on Pages without grpc_frame installed.
autodoc_mock_imports = [
    "grpc_frame",
    "grpc_frame.grpc_client",
    "grpc_frame.grpc_server",
]

html_theme = "sphinx_rtd_theme"

exclude_patterns = [
    "_build",
]
