import subprocess
import sys

from odooss.utils import write_file


def create_requirement(path: str):
    content = """\
ruff>=0.12.8
pre-commit>=3.8.0
"""
    file_name = "requirements.txt"
    write_file(path, content, filename=file_name)

    # Run pip via current Python interpreter
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", file_name], cwd=path, check=True
    )


if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    create_requirement(path)
