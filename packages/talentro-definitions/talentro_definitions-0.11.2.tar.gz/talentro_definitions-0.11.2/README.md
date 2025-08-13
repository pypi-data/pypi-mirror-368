# Talentro definitions

This package contains all models and data structures for Talentro
It is exclusively meant for the Talentro ecosystem.

## How to create a new version

- Make changes in the code, like editing the models
- Bump the version number to desired version in `pyproject.toml` using the `major.minor.fix` format
- run `poetry build`
- run `poetry publish`

Now a new version is uploaded to pypi and you can install it after a minute in the other projects.