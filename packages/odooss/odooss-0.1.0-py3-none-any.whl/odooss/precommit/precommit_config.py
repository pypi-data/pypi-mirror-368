import subprocess
from odooss.utils import write_file


def create_precommit_config(path: str):
    content="""\
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.4  # Use latest version
    hooks:
      - id: ruff
        name: Ruff Linter for Odoo
        args: [ --fix, ]# Optional: auto-fix on dev machines
        files: ^addons/

      - id: ruff-format
        name: Ruff Formatter
        files: ^addons/"""
    write_file(path, content, filename=".pre-commit-config.yaml")


def install_precommit(path: str):
    # Change directory to target path and run the commands
    try:
        subprocess.run(["pre-commit", "install"], cwd=path, check=True)
        subprocess.run(["pre-commit", "run", "--all-files"], cwd=path, check=True)
        print("pre-commit installed and ran successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running pre-commit commands: {e}")

if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    create_precommit_config(path)