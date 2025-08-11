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
      # Step 1: Checkout repo
      - name: Checkout code
        uses: actions/checkout@v3

      # Step 2: Get last commit message
      - name: Get latest commit message
        id: get_commit
        run: |
          echo "message<<EOF" >> $GITHUB_OUTPUT
          git log -1 --pretty=%B >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      # Step 3: Extract modules from commit message
      - name: Extract modules from commit message
        id: extract_modules
        run: |
          echo "Commit message:"
          echo "${{ steps.get_commit.outputs.message }}"
          message="${{ steps.get_commit.outputs.message }}"
          # Extract after #odoo-module: and replace commas with spaces
          modules=$(echo "$message" | sed -n 's/.*#odoo-module:\([^ ]*\).*/\1/p' | tr ',' ' ' || true)
          if [ -z "$modules" ]; then
            echo "No modules found to update."
            modules=""
          fi
          echo "modules=$modules" >> $GITHUB_OUTPUT

      # Step 4: Debug
      - name: Debug extracted modules
        run: |
          echo "Modules extracted: '${{ steps.extract_modules.outputs.modules }}'"

      # Step 5: SSH to remote and update modules
      - name: SSH into server and update modules
        if: steps.extract_modules.outputs.modules != ''
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${{ secrets.REMOTE_HOST }}
          username: ${{ secrets.REMOTE_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          port: 22
          script: |
            cd ${{ secrets.SSH_FILE_PATH }}
            echo "Pulling latest code from branch ${{ github.ref_name }}..."
            git fetch origin ${{ github.ref_name }}
            git checkout ${{ github.ref_name }}
            git pull origin ${{ github.ref_name }}
            echo "Updating modules: ${{ steps.extract_modules.outputs.modules }}"
            docker compose run web odoo -u ${{ steps.extract_modules.outputs.modules }} -d ${{ secrets.ODOO_DB_NAME }} --stop-after-init --no-http
    """
    write_file(path, content, filename=".github/ci_cd.yml")


if __name__ == "__main__":
    path = "/home/agga/Documents/odoo-dev/ica_standard_structure/test"
    create_github_workflow(path)
