# 07. Python dependencies with known vulnerabilities

| | |
|---|---|
| Severity | High |
| OWASP Top 10 (2021) | A06 Vulnerable and Outdated Components |
| Where | `backend/requirements.txt` |
| Issue | [LuisDulo/smart-school-feeding#115](https://github.com/LuisDulo/smart-school-feeding/issues/115) |
| Fix | [LuisDulo/smart-school-feeding#125](https://github.com/LuisDulo/smart-school-feeding/pull/125) |
| Status | Fixed |

## What was wrong

pip-audit found 49 known vulnerabilities in five pinned packages. The full list is in [evidence/pip-audit-before.txt](../evidence/pip-audit-before.txt).

| Package | Pinned | Advisories | Fixed in | Exposure in this app |
|---|---|---|---|---|
| djangorestframework | 3.18.1 | 3 | 3.18.2 | High. One lets an unauthenticated client get past Django's `DATA_UPLOAD_MAX_MEMORY_SIZE` and force a large allocation; another is unbounded `Accept` header parsing. Every API request goes through DRF, and login is public. |
| PyJWT | 2.14.0 | 2 | 2.15.0 | Medium. Pulled in by SimpleJWT, which verifies every token. |
| urllib3 | 2.7.0 | 3 | 2.8.0 | Medium. Used by `requests` for Daraja and Expo calls. |
| certifi | 2026.7.22 | 1 | 2026.10.18 | Low. The bundle still trusted a distrusted root certificate. |
| Pillow | 12.3.0 | 39 | 13.0.0 | Low. Image decoder bugs, but the app takes no image uploads. Pillow is only used through matplotlib, reportlab and fpdf2 to draw charts and PDFs. |

High overall, because DRF sits in front of every endpoint and the first DRF advisory needs no account.

## Fix

Each package moved to its first fixed release. `pip check` reports no conflicts, and the full test suite passes (244 tests). pip-audit now reports no known vulnerabilities, and CI fails the build if a new one appears ([11](11-no-ci.md)).
