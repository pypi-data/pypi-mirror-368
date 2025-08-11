from odooss.utils import write_file


def create_github_workflow(path: str):
    content = """\
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
        run: echo "${{ secrets.ODOO_DB_PASSWORD }}" > odoo_pg_pass

      - name: Create config directory and odoo.conf
        run: |
          mkdir -p config
          cat > config/odoo.conf <<EOF
          [options]
          ; This is the Odoo configuration file
          admin_passwd=master
          db_name=${{ secrets.ODOO_DB_NAME }}
          addons_path = /mnt/extra-addons
          EOF

      - name: Start Docker Compose
        run: docker compose up -d

      - name: Wait for Odoo to be ready
        run: |
          echo "Waiting for Odoo to start..."
          timeout=300
          interval=5
          elapsed=0
          while ! docker compose exec web curl -s http://localhost:8069 > /dev/null; do
            if [ $elapsed -ge $timeout ]; then
              echo "Timeout waiting for Odoo to start."
              exit 1
            fi
            echo -n "."
            sleep $interval
            elapsed=$((elapsed + interval))
          done
          echo "Odoo is ready."

      - name: Get latest commit message
        id: get_commit
        run: |
          echo "message<<EOF" >> $GITHUB_OUTPUT
          git log -1 --pretty=%B >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Extract modules from commit message
        id: extract_modules
        run: |
          echo "Commit message:"
          echo "${{ steps.get_commit.outputs.message }}"
          modules=$(echo "${{ steps.get_commit.outputs.message }}" | sed -n 's/.*#odoo-module:\\([^ ]*\\).*/\1/p' || true)
          if [ -z "$modules" ]; then
            echo "No modules found to update."
            modules=""
          fi
          echo "modules=$modules" >> $GITHUB_OUTPUT

      - name: Debug extracted modules
        run: |
          echo "Modules extracted: '${{ steps.extract_modules.outputs.modules }}'"

      - name: Update Odoo modules inside container
        if: steps.extract_modules.outputs.modules != ''
        run: |
            echo "Updating modules: ${{ steps.extract_modules.outputs.modules }}"
            docker compose exec web odoo -u ${{ steps.extract_modules.outputs.modules }} -d ${{ secrets.ODOO_DB_NAME }} --stop-after-init --no-http

      - name: Shutdown Docker Compose
        if: always()
        run: docker compose down
    """
    write_file(path, content, filename=".github/ci_cd.yml")


if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    create_github_workflow(path)
