
# Odoo Standard Scaffold


```zsh
 odooss create <your-dir-path> --odoo_version 18.0 --python 3.10 --vcs github
```

- ```--odoo_version``` - for odoo docker image tag
- ```--python``` - for python-<version>-slim docker image tag
- ```--vcs``` - for version control system (e.g. github, gitlab, bitbucket, etc...)

## output will be like this

- addons/
  - README.md
- .dockerignore
- .gitignore
- .pre-commit-config.yaml
- compose.yml
- Dockerfile
- README.md
- requirements.txt
- ruff.toml

## and then create currently dir in `config/odoo.conf` file.

```
[options]
admin_passwd=xxxx
addons_path=/mnt/extra-addons
```

## create `odoo_pg_pass` file
```
your-password=xxxx
```

## add your repo (optional).
```zsh
git remote add origin <repo-url>
```

## check your code format using ruff.

```zsh
ruff format
```

# check your code and fixed it. 
`ruff` can check and auto fix for some and others for manually.
```
ruff check --fix
```

## now you can push to your branch. 
if pushing was failed. you need to check with `ruff` again.

```zsh
git add .
git commit -m "[ADD] project initalize"
git push origin <branch>
```
### if you are using automaion flow. like `github` action need to follow instructions.

## Github
### Settings >> Security >> Actions secrets and variables >> secrets >> Repository secrets
#### add this variables
- `ODOO_DB_NAME`
- `ODOO_DB_PASSWORD`
- `REMOTE_HOST` - <your-server-ip> 192.169.100.1
- `REMOTE_USER` - ubuntu or root
- `SSH_FILE_PATH` - /root/your-project/
- `SSH_PRIVATE_KEY` - server access private key

now you can use smart commands and add in git commit message like this -

```
[ADD] res.partner model in age fields. #odoo-module:contacts,sale
```

#### now git push and check your github action.

# we  will be continue for other vcs (like gitlab, bitbucket, etc....) in the future

###  Agga, IdeaCode Academy