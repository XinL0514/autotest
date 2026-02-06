# Repository Guidelines

## Project Structure & Module Organization
This repository is a Python UI automation framework built with Playwright + Pytest and follows a Page Object Model (POM) structure.

- `pages/`: page objects and reusable page actions (`pages/base_page.py`, `pages/common/`, `pages/modules/`).
- `tests/`: test suites grouped by business module (`tests/login/`, `tests/mar/`, `tests/blood/`).
- `test_data/`: YAML test data files matching module names (for example, `test_data/login/login_data.yaml`).
- `utils/`: shared helpers (assertion wrapper, logging, data loader).
- `config/`: runtime configuration (`config/config.py`).
- `docs/`: troubleshooting and debugging guides.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: create and activate local virtualenv.
- `pip install -r requirements.txt`: install Python dependencies.
- `playwright install`: install browser binaries.
- `pytest`: run all tests using defaults from `pytest.ini` (Chromium, headed, Allure output).
- `pytest tests/login/test_login.py -v -s`: run one test file with verbose console logs.
- `pytest tests/mar/ --trace-mode=retain-on-failure`: keep Playwright trace only for failures.
- `allure serve allure-results`: view Allure report locally.

## Coding Style & Naming Conventions
- Use 4-space indentation, explicit imports, and type hints where practical.
- File names and functions use `snake_case`; classes use `PascalCase`; test classes start with `Test`.
- New page classes must inherit `BasePage` and keep locators/actions inside page objects.
- Use `utils.assertion.Assertion` methods for checks instead of raw `assert` in test cases.
- Load test data through `DataLoader.get_test_data()` rather than hardcoding values.

## Testing Guidelines
- Framework: `pytest` + `pytest-playwright` + `allure-pytest`.
- Naming is enforced by `pytest.ini`: `test_*.py`, `Test*`, and `test_*` methods.
- Use `page` fixture for unauthenticated flows; use `authenticated_page` for logged-in scenarios.
- Add/update tests with every behavior change; keep test data close to the related module.

## Commit & Pull Request Guidelines
- Current history includes short messages (for example, `fix bug`, `update CLAUDE.md`) and Chinese summaries; prefer clearer, scoped messages like `mar: add tab switch test`.
- Keep each commit focused on one logical change.
- PRs should include: purpose, changed paths, test command(s) run, and evidence (Allure screenshot/log) for UI-impacting updates.

## Security & Configuration Tips
- Do not commit secrets, real credentials, or sensitive cookies.
- Review `test_data/auth_state.json`, `logs/`, and generated artifacts (`allure-results/`, `allure-report/`) before pushing.
- Keep environment-specific values in `config/config.py` and avoid hardcoding URLs in tests.
