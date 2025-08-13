# Django Accounts API

Scenario to support is a compiled javascript capable frontend needing to provide authentication features over api

Caveat enptor, very early days, still being tested in its first project

# Requirements
- Python 3.7 - 3.12
- Django 3.2 - 4

# Usage

- `pip install ...` or equivalent
- add `'django_accounts_api',` to INSTALLED_APPS
- add `path('/accounts_api/', include('django_accounts_api.urls'))` to your urls
- implement your frontend to use the urls

## Features

See docs...


## Development
1. Install Poetry https://python-poetry.org/docs/#installation

2. Use a virtual environment https://python-poetry.org/docs/basic-usage/#using-your-virtual-environment

3. `poetry install --with dev --no-root` installs dependencies for development

4. `poetry run pre-commit install` installs the pre-commit hooks

5. `pytest` runs tests

* To install poetry you may want to `pipx install poetry` and/or `pipx upgrade poetry`

### Publishing

Create a Pypi token perhaps at https://pypi.org/manage/account/token/
It should look like this

```
Create API token
Token for "django_accounts_api"

Permissions: Upload packages
Scope: Project "django-accounts-api"

pypi-<YOUR_KEY>
```

`poetry config pypi-token.pypi pypi-<YOUR_KEY>`

Bump the `version` number
Run `poetry lock` if requirements have changed
Run `poetry build`
Run `poetry publish`

### Tox

To run tox you will need to make sure that the range of python versions required are available for tox to use.

Recommendation: use pyenv
- `pyenv install 3.7 3.8 3.9 3.10 3.11`
- `pyenv local  3.7 3.8 3.9 3.10 3.11`
- `tox`

### Documentation

- `cd docs`
- `make html`

TODO: add to tox

### Linting & formatting

TODO: add to tox
