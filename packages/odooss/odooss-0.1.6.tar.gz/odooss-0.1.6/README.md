
# Odoo Standard Scaffold


```zsh
 odooss create <your-dir-path> --odoo_version 18.0 --python 3.10
```

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

# Agga, IdeaCode Academy