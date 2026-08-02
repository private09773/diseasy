# Contributing to Diseasy

Thanks for considering a contribution! A few guidelines to keep things smooth:

## Getting Started
1. Fork the repo and clone your fork.
2. Install dev dependencies: `pip install -r requirements-dev.txt`
3. Create a branch: `git checkout -b fix/short-description`

## Code Style
- Follow PEP 8; run `ruff check .` before committing.
- Type hints are required on public functions.
- Keep the `.` `[]` `()` `<>` `{}` notation spec (`docs/notation_spec.md`) in sync
  with any API changes.

## Tests
- Add/update tests in `tests/` for any behavior change.
- Run `pytest` before opening a PR.

## Pull Requests
- Keep PRs focused on one change.
- Reference related issues.
- Update `CHANGELOG.md` under "Unreleased."

## Reporting Bugs
Use the issue templates under `.github/ISSUE_TEMPLATE/`.