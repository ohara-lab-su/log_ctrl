from pathlib import Path
import os
import sys

DOCS_DIR = Path(__file__).resolve().parent
ROOT_DIR = DOCS_DIR.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

project = "log_ctrl"
author = "Kengo NAKADA"
language = os.environ.get("DOCS_LANGUAGE", "en")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
myst_enable_extensions = ["deflist", "colon_fence", "linkify"]
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_typehints = "description"
autodoc_preserve_defaults = True
autodoc_mock_imports = ["grpc_frame", "grpc_frame.grpc_client", "grpc_frame.grpc_server"]
html_theme = "sphinx_rtd_theme"
exclude_patterns = ["_build"]
