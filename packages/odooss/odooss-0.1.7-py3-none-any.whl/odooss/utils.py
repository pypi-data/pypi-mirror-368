import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def write_file(path: str, content: str, filename: str):
    full_path = os.path.join(path, filename)
    dir_path = os.path.dirname(full_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")

    logger.info(f"Writing file to {full_path}")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    content = "Hello, this is a test."
    filename = "test.txt"
    write_file(path, content, filename)
