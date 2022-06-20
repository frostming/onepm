# onepm

Picks the right package manager for you

Don't make me think about which package manager to use when I clone a project from other people. OnePM will pick the right package manager by searching for the lock files and/or the project settings in `pyproject.toml`.

This project is created in the same spirit as [@antfu/ni](https://www.npmjs.com/package/@antfu/ni).

Supported package managers: [pip], [pipenv], [poetry], [pdm]

[pip]: https://pypi.org/project/pip/
[pipenv]: https://pypi.org/project/pipenv/
[poetry]: https://pypi.org/project/poetry/
[pdm]: https://pypi.org/project/pdm/

## Provided Shortcuts

### `pi` - install

```
pi

# (venv) pip install . or pip install -r requirements.txt
# pipenv install
# poetry add
# pdm add
```

```
pi requests

# (venv) pip install requests
# pipenv install requests
# poetry add requests
# pdm add requests
```

### `pu` - update

```
pu

# not available for pip
# pipenv update
# poetry update
# pdm update
```

### `pr` - run

```
pr command ...args

# (venv) command ...args
# pipenv run command ...args
# poetry run command ...args
# pdm run command ...args
```

### `pun` - uninstall

```
pun requests

# pip uninstall requests
# pipenv uninstall requests
# poetry remove requests
# pdm remove requests
```

### `pa` - Alias for the package manager

```
pa

# pip
# pipenv
# poetry
# pdm
```

If the package manager agent is pip, **OnePM will enforce an activated virtualenv, or a `.venv` under the current directory**.
