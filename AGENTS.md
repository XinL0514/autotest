# Repository Guidelines

## Project Structure & Module Organization
This repository is a Python UI automation framework built with Playwright + Pytest and follows a Page Object Model (POM) structure.

- `fixtures/`: shared fixture helpers (`page_factory.py`) and business auth fixtures (`business_auth.py`).
- `pages/`: page objects and reusable actions.
- `pages/base_page.py`: base page class, composed via mixins in `pages/mixins/`.
- `pages/common/`: shared business pages (for example `login/`).
- `pages/modules/`: module pages (`mar/`, `blood/`, `test/`).
- `tests/`: pytest suites by module (`tests/login/`, `tests/mar/`, `tests/blood/`, `tests/test/`).
- `tests/conftest.py`: exposes business auth fixtures to the `tests/` tree.
- `test_data/`: YAML test data (`test_data/login/login_data.yaml`, `test_data/mar/mar_data.yaml`, `test_data/blood/blood_data.yaml`).
- `conftest.py`: root-level shared fixtures for browser/page setup, tracing, failure screenshot + allure attachments.
- `utils/`: shared helpers (`assertion.py`, `data_loader.py`, `logger.py`, etc.).
- `config/config.py`: base URL, timeout, headless and logging config.
- `docs/`: debugging and framework design documents.

## Build, Test, and Development Commands
- `python3 -m venv venv && source venv/bin/activate`: create and activate local virtualenv (this repo currently uses `venv/`).
- `pip install -r requirements.txt`: install dependencies.
- `playwright install`: install browser binaries.
- `pytest`: run all tests using discovery defaults from `pytest.ini`; browser mode falls back to `config/config.py` unless CLI options override it.
- `pytest tests/login/test_login.py -v -s`: run one file with verbose console output.
- `pytest tests/mar/ --trace-mode=retain-on-failure`: keep trace zip only on failure.
- `pytest tests/blood/test_blood_submit.py --trace-mode=on`: always keep trace for this test file.
- `allure serve allure-results`: open local Allure report.
- `playwright show-trace test-results/<trace.zip>`: inspect saved trace.

## Coding Style & Naming Conventions
- Use 4-space indentation and explicit imports; add type hints where practical.
- File and function names use `snake_case`; classes use `PascalCase`; test classes start with `Test`.
- New page classes should inherit `BasePage`; keep selectors and page operations in page objects, not test bodies.
- Reuse base mixins and existing wrappers before adding duplicate low-level Playwright calls.
- Use `utils.assertion.Assertion` in test cases instead of raw `assert`.
- Load data via `DataLoader.get_test_data("<module>/<file>.yaml", "<key>")`; do not hardcode test values in tests.

## Testing Guidelines
- Framework stack: `pytest` + `pytest-playwright` + `allure-pytest`.
- Naming is enforced by `pytest.ini`: `test_*.py`, `Test*`, and `test_*`.
- Use `page` fixture for unauthenticated flows.
- Use `authenticated_page` fixture for business flows that require login; session-level auth state is managed by `authenticated_state`.
- `authenticated_page` / `authenticated_state` are implemented in `fixtures/business_auth.py` and imported into the test tree by `tests/conftest.py`.
- Auth state files are saved under `test_data/` as `auth_state.json`; when running with xdist, files are worker-isolated as `auth_state_<worker>.json`.
- `--trace-mode` supports: `off` (default), `on`, `retain-on-failure`.
- On failure, root `conftest.py` auto-attaches screenshot and URL to Allure; trace files are attached when generated.
- Keep test data close to the module and update tests with each behavior change.

## Commit & Pull Request Guidelines
- Prefer clear, scoped commit messages, e.g. `mar: add medication delete assertion`.
- Keep each commit focused on one logical change.
- PRs should include:
  - purpose and scope,
  - changed paths,
  - test commands executed,
  - evidence for UI-impacting changes (Allure screenshot / trace / logs).

## Security & Configuration Tips
- Do not commit real credentials, tokens, or sensitive cookies.
- Review sensitive/generated files before pushing:
  - `test_data/auth_state*.json`
  - `test_data/login_debug.png`, `test_data/login_error.png`
  - `logs/`
  - `allure-results/`, `allure-report/`
  - `test-results/`
- Keep environment values in `config/config.py`; avoid hardcoding URLs or credentials in tests/page objects.
