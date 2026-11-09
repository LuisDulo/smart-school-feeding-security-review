# 11. No CI, so nothing stopped a fixed bug from returning

| | |
|---|---|
| Severity | Process |
| OWASP Top 10 (2021) | A05 Security Misconfiguration (missing security controls in the pipeline) |
| Where | `.github/workflows/` (did not exist) |
| Issue | [LuisDulo/smart-school-feeding#117](https://github.com/LuisDulo/smart-school-feeding/issues/117) |
| Fix | [LuisDulo/smart-school-feeding#127](https://github.com/LuisDulo/smart-school-feeding/pull/127) |
| Status | Fixed |

## What was wrong

The app had a good test suite of more than 200 tests, but it ran only when someone remembered to run it locally. Dependency scans did not run at all.

A security fix is only as durable as the check that keeps it in place. Without CI:

- a later change to the callback could quietly undo [01](01-forged-mpesa-callback.md)
- a new advisory against a pinned package would go unnoticed

## Fix

`.github/workflows/ci.yml` runs on every push to main and every pull request.

| Job | Checks | Fails on |
|---|---|---|
| Backend (PostgreSQL 16, Python 3.12) | `manage.py check`, the full test suite (including every `test_security_*` file and `check --deploy` with production settings), `pip-audit` | any failing test, any known vulnerability in `requirements.txt` |
| Backend static analysis | `bandit` on the app packages | any medium or high issue |
| Dashboard and mobile | `npm audit --omit=dev` | any critical advisory |

The workflow uses only throwaway values, such as a CI-only `SECRET_KEY` and the Postgres service password, and runs with `DEBUG` off, as in production. Its token has read-only access to the repository.
