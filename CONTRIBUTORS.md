## High-level Guidelines

Thank you for your interest in contributing to this repository. To help maintain
the quality of the codebase and ensure a quick review of your pull request, you
should:

1. Write clear, clean code and format it in line with the style used in the 
repository.
2. Leave comments, and use docstrings where appropriate.
3. Add unit tests for any new functionality you introduce, if a set of test cases
are already set up in the repository.
4. Use git commit messages to leave an informative trace of what additions and
changes were made.
5. Write an informative high level description of the pull request, changes made,
and the reason for these changes before submitting the pull request.

If you have not signed our Contributor License Agreement, you will be asked to
sign one by our automated system when you submit your first pull request to
a Cohere repository.

## Pro-tips
- Set up a new `git branch` for any additional work and make a PR back to `main`. :)
- Tests should be added using `pytest` alongside feature development. PRs require good test coverage before they are approved.
- Aim to include a single change in each commit. Commit messages should be descriptive and start with action verbs.
- Try to keep PRs as small as possible, ideally with one feature per PR. This makes PRs easier to review and faster to merge. 
- Use the `typing` module to define typing signatures for all functions you define.
- Write Google-style docstrings for all functions created, explaining its description, the arguments, and return value.
- Use expressive and descriptive variable and function names.

## Full Walkthrough

Obtain the `conversant` source code from Github:
```
git clone git@github.com:cohere-ai/sandbox-conversant.git
cd sandbox-conversant
```

We use `conda` as an environment manager, `pip` as the package installer, and `poetry` as a dependency manager. For more information, please read this [guide](https://ealizadeh.com/blog/guide-to-python-env-pkg-dependency-using-conda-poetry). 

Create the `conda` environment:
```
conda create -n conversant python=3.8.10
```

Activate the `conversant` environment:
```
conda activate conversant
```

Install `poetry`:
```
pip install poetry==1.2.0
```

Set `poetry` to use the Python installed in the `conversant` environment:
```
poetry env use $(which python)
```

Install all dependencies specified in `pyproject.toml`, including dev dependencies:
```
poetry install
```

Once the `conversant` poetry environment is setup, each command needs to be prefixed with `poetry run` so it can run in that poetry environment. The following command can be run to spawn a [shell](https://python-poetry.org/docs/cli/#shell) so that commands can be run without this prefix:
```
poetry shell
```

Commands from hereon assume that `poetry shell` has been run. We use git `pre-commit` hooks, such that a commit will fail if any of the checks defined in `.pre-commit-config.yaml` fail. We also use `black` as the formatter, `ruff` as the linter, and `pytest` for testing:
```
pre-commit install
black .
ruff .
pytest
```

Documents can be built using `pdoc` as follows:
```
pdoc conversant -o docs/ --docformat google
```