# onepm

Picks the right package manager for you

Don't make me think about which package manager to use when I clone a project from other people. OnePM will pick the right package manager by searching for the lock files and/or the project settings in `pyproject.toml`.

This project is created in the same spirit as [@antfu/ni](https://www.npmjs.com/package/@antfu/ni).

Supported package managers: [pip], [pipenv], [poetry], [pdm]

[pip]: https://pypi.org/project/pip/
[pipenv]: https://pypi.org/project/pipenv/
[poetry]: https://pypi.org/project/poetry/
[pdm]: https://pypi.org/project/pdm/

## Install onepm

Install with `pipx`:

```bash
pipx install onepm
```

Or use pdm global install:

```bash
pdm add -g onepm
```

## Provided Shortcuts

### `pi` - install

```bash
pi

# (venv) pip install . or pip install -r requirements.txt
# pipenv install
# poetry install
# pdm install
```

```bash
pi requests

# (venv) pip install requests
# pipenv install requests
# poetry add requests
# pdm add requests
```

### `pu` - update

```bash
pu

# not available for pip
# pipenv update
# poetry update
# pdm update
```

### `pr` - run

```bash
pr ...args

# (venv) ...args
# pipenv run ...args
# poetry run ...args
# pdm run ...args
```

### `pun` - uninstall

```bash
pun requests

# pip uninstall requests
# pipenv uninstall requests
# poetry remove requests
# pdm remove requests
```

### `pa` - Alias for the package manager

```bash
pa

# pip
# pipenv
# poetry
# pdm
```

If the package manager agent is pip, **OnePM will enforce an activated virtualenv, or a `.venv` under the current directory**.
