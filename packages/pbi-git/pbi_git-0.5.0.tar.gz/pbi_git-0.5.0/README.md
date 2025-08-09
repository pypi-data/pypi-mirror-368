# Overview


[![PyPI Downloads](https://static.pepy.tech/badge/pbi-git)](https://pepy.tech/projects/pbi-git)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
[![Coverage Status](https://coveralls.io/repos/github/douglassimonsen/pbi_git/badge.svg?branch=main)](https://coveralls.io/github/douglassimonsen/pbi_git?branch=main)
![Repo Size](https://img.shields.io/github/repo-size/douglassimonsen/pbi_git)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fdouglassimonsen%2Fpbi_git.svg?type=shield&issueType=license)](https://app.fossa.com/projects/git%2Bgithub.com%2Fdouglassimonsen%2Fpbi_git?ref=badge_shield&issueType=license)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fdouglassimonsen%2Fpbi_git.svg?type=shield&issueType=security)](https://app.fossa.com/projects/git%2Bgithub.com%2Fdouglassimonsen%2Fpbi_git?ref=badge_shield&issueType=security)

Read the [documentation](https://douglassimonsen.github.io/pbi_git/) for more information.


# Dev Instructions


## Virtual Environment

```shell
python -m venv venv
venv\Scripts\activate
python -m pip install .[dev]
# pre-commit install
```

## Building package

```shell
python -m build .
```

## Running the Documentation Server

```shell
python -m pip install .[docs]
mkdocs serve -f docs/mkdocs.yml
```

## Deploy docs to Github Pages

```shell
mkdocs  gh-deploy --clean -f docs/mkdocs.yml
```