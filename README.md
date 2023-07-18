# Face Embeddings

## Installation DEV steps

```sh
python3.10 -m pip install --upgrade pip
python3.10 -m pip install pipenv --upgrade
pipenv --python 3.10
pipenv shell
pipenv install (run `pipenv install -d` for local development)
```

## Configuring [Pre-Commit](https://pre-commit.com/)

Please make sure to run following commands before starting any development.

```sh
pre-commit install --hook-type pre-commit
pre-commit install --hook-type pre-push
sh cmd/install_hooks.sh
```
