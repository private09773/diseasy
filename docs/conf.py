"""Sphinx configuration for Diseasy's documentation."""
project = "Diseasy"
copyright = "2026, Diseasy Contributors"
author = "Diseasy Contributors"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
