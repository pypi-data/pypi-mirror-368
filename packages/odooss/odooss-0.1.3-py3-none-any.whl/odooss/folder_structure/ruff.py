from odooss.utils import write_file


def create_ruff(path: str):
    content = """\
[lint]
select = [
    "E",    # pycodestyle
    "F",    # Pyflakes
    "W",    # pycodestyle warnings
    "N",    # pep8-naming (naming conventions)
    "B",    # flake8-bugbear (code smells & unsafe patterns)
    "T201", # print()
    "UP",   # pyupgrade (old syntax like Python 2-style code)
    "PLC",  # pylint-convention
    "PLE",  # pylint-error
    "PLR",  # pylint-refactor
    "PLW",  # pylint-warning
]
fixable = ["ALL"]


ignore = [
    "E501", # line too long
    "E301", # expected 1 blank line, found 0
    "E302", # expected 2 blank lines, found 1
    "PLR0913", #  Too many arguments
]

[lint.per-file-ignores]
"__init__.py" = [
    "F401", # import but unused
]
"__manifest__.py"=[
    "B018",# useless expression.
]
"""
    write_file(path, content, filename="ruff.toml")


if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    version = 18.0
    python = 3.10
    create_ruff(path)
