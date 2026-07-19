# Tech Stack

- Python package and optional Flask-based Web API.
- NumPy-backed computation; pytest, mypy, Black, Flake8, Pylint, and isort.
- setuptools packaging for pip and Conda recipes for Conda builds.
- GNU Make task entry points and GitHub Actions hosted CI.
- Git with GitHub Flow against `master`.

Authoritative dependency and interpreter constraints remain in `setup.py`,
`setup.cfg`, `pyproject.toml`, and the workflow files under `.github/workflows/`.
