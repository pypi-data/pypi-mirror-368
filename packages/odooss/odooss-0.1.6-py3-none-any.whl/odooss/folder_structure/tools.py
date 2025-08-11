from odooss.utils import write_file


def create_addons(path: str):
    write_file(path, "", filename="addons/README.md")


def create_readme(path: str):
    content = "# Powered by IdeaCode Academy"
    write_file(path, content, filename="README.md")


if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    version = 18.0
    python = 3.10
    create_addons(path)
    create_readme(path)
