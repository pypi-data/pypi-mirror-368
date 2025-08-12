"""Generate the code reference pages."""

from __future__ import annotations

import tomllib
from pathlib import Path

import mkdocs_gen_files

# Load project scripts from pyproject.toml
with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)
scripts = pyproject["project"]["scripts"]

# Create a page for each script
for script_name in scripts:
    # Example: loancalc = "hyperskill_python_portfolio.loancalc.main:main"
    module_path_str = scripts[script_name].split(":")[0]
    # -> "hyperskill_python_portfolio.loancalc.main"

    doc_path = Path("reference", f"{script_name}.md")
    # -> reference/loancalc.md

    with mkdocs_gen_files.open(doc_path, "w") as f:
        print(f"# {script_name.title()}", file=f)
        # This will embed the docstrings from the module into the page
        print(f"::: {module_path_str}", file=f)

    mkdocs_gen_files.set_edit_path(doc_path, "pyproject.toml")
