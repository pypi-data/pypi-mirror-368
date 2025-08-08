from odooss.utils import write_file


def create_dockerfile(path: str, odoo_version: float, python: float):
    content = f"""# Stage 1: Build Dependencies
FROM python:{python}-slim AS builder

WORKDIR /opt/odoo

# Copy and install Python dependencies
COPY ./requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Stage 2: Final Image with Odoo
FROM odoo:{odoo_version}

USER root

# Copy only necessary files from the builder stage
COPY --from=builder /opt/odoo /opt/odoo

# Copy custom addons
COPY ./addons /mnt/extra-addons

USER odoo
"""
    write_file(path, content, filename="Dockerfile")


def create_docker_compose(path):
    content = """\
version: '3.1'
services:
  web:
    build:
      context: .
    depends_on:
      - db
    ports:
      - "9000:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./config:/etc/odoo
    environment:
      - PASSWORD_FILE=/run/secrets/postgresql_password
    secrets:
      - postgresql_password
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD_FILE=/run/secrets/postgresql_password
      - POSTGRES_USER=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - odoo-db-data:/var/lib/postgresql/data/pgdata
    secrets:
      - postgresql_password
volumes:
  odoo-web-data:
  odoo-db-data:

secrets:
  postgresql_password:
    file: odoo_pg_pass
    """
    write_file(path, content, filename="compose.yml")


def create_dockerignore(path: str):
    content = """\
# Include any files or directories that you don't want to be copied to your
# container here (e.g., local build artifacts, temporary files, etc.).
#
# For more help, visit the .dockerignore file reference guide at
# https://docs.docker.com/go/build-context-dockerignore/

**/.DS_Store
**/__pycache__
**/.venv
**/.classpath
**/.dockerignore
**/.env
**/.git
**/.gitignore
**/.project
**/.settings
**/.toolstarget
**/.vs
**/.vscode
**/*.*proj.user
**/*.dbmdl
**/*.jfm
**/bin
**/charts
**/docker-compose*
**/compose.y*ml
**/Dockerfile*
**/node_modules
**/npm-debug.log
**/obj
**/secrets.dev.yaml
**/values.dev.yaml
LICENSE
README.md
"""
    write_file(path, content, filename=".dockerignore")


if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    version = 18.0
    python = 3.10
    create_dockerfile(path, version, python)
    create_docker_compose(path)
    create_dockerignore(path)
