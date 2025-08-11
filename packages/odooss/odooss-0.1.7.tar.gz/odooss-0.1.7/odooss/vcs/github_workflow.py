from odooss.utils import write_file


def create_github_workflow(path:str):
    content="""\
    name: Odoo Modules Update with Docker Compose

on:
  push:
    branches:
      - main

jobs:
  update-modules:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Create odoo_pg_pass secret file
        run: echo "odoo" > odoo_pg_pass

      - name: Create config directory and odoo.conf
        run: |
          mkdir -p config
          cat > config/odoo.conf <<EOF
          [options]
          ; This is the Odoo configuration file
          admin_passwd=master
          db_name=odoo
          addons_path = /mnt/extra-addons
          EOF

      - name: Start Docker Compose
        run: docker compose up -d

      - name: Wait for Odoo to be ready
        run: |
          echo "Waiting for Odoo to start..."
          until docker compose exec web curl -s http://localhost:8069 > /dev/null; do
            echo -n "."
            sleep 5
          done
          echo "Odoo is ready."

      - name: Get latest commit message
        id: get_commit
        run: echo "message=$(git log -1 --pretty=%B)" >> $GITHUB_OUTPUT

      - name: Extract modules from commit message
        id: extract_modules
        run: |
          echo "Commit message: ${{ steps.get_commit.outputs.message }}"
          modules=$(echo "${{ steps.get_commit.outputs.message }}" | grep -oP '(?<=#odoo-module:)[\w,]+')
          echo "modules=$modules" >> $GITHUB_OUTPUT

      - name: Update Odoo modules inside container
        if: steps.extract_modules.outputs.modules != ''
        run: |
          echo "Updating modules: ${{ steps.extract_modules.outputs.modules }}"
          docker compose run web odoo -u ${{ steps.extract_modules.outputs.modules }} -d odoo --stop-after-init --no-http

      - name: Shutdown Docker Compose
        if: always()
        run: docker compose down
    """
    write_file(path, content, filename=".github/ci_cd.yml")

if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    create_github_workflow(path)
