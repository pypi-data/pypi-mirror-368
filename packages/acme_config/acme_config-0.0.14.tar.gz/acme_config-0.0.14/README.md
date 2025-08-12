# acme-config

## Description

System to store application configuration

## Motivation

To support a release system that can store references to various application artifacts we need a config system that can store environment variables needed by a specific application (i.e. what is put into `.env` file). Specifically, we want to make the configurations immutable so once they are refered to from a release system they won't change.


## Features

* Uses AWS Parameter Store as a storage layer for parameters
* Enforces each parameter needs to be assigned to an application identifier (`app-name`), an environment identifier (`env`) and a integer version (`ver-number`)
* Once parameters are written with such combination of identifiers `acme-config` prevents from overwriting them.
* Allows to retreive parameters for a given combination of (`app-name`, `env` and `ver-number`) and stores it in a local file in `.env` file format convenient for editing.
* Allows to set parameters from `.env` file specified at a file path.
* Each (app-name, env) combination can set a default version number. This can be set with `set-version` command
* Default version can be retrieved with `get-version` command. Value will be put to `stdout`.

## Example usage

Requires setup of a default AWS profile e.g. via `aws sso login`. Can be specified via `AWS_PROFILE` env var.

## To set

    ac set -app-name acme-config -env dev -ver-number 1 --params-path .env

## To set default version

    ac set-version -app-name acme-config -env dev -ver-number 1

## To get default version

    ac get-version -app-name acme-config -env dev

### To fetch

    ac fetch -app-name acme-config -env dev -ver-number 1

Will save parameters to a file `acme-config.dev.1.env`

# Dev environment

The project comes with a python development environment.
To generate it, after checking out the repo run:

    chmod +x create_env.sh

Then to generate the environment (or update it to latest version based on state of `uv.lock`), run:

    ./create_env.sh

This will generate a new python virtual env under `.venv` directory. You can activate it via:

    source .venv/bin/activate

If you are using VSCode, set to use this env via `Python: Select Interpreter` command.

# Project template

This project has been setup with `acme-project-create`, a python code template library.

# Required setup post use

* Enable GitHub Pages to be published via [GitHub Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#publishing-with-a-custom-github-actions-workflow) by going to `Settings-->Pages-->Source`
* Create `release` environment for [GitHub Actions](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment#creating-an-environment) to enable uploads of the library to PyPi
* Setup auth to PyPI for the GitHub Action implemented in `.github/workflows/release.yml`: [Link](https://docs.pypi.org/trusted-publishers/adding-a-publisher/) `uv publish` [doc](https://docs.astral.sh/uv/guides/publish/#publishing-your-package)