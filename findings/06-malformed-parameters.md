# 06. Malformed query parameters crash endpoints

| | |
|---|---|
| Severity | Low |
| OWASP Top 10 (2021) | A04 Insecure Design (missing input validation) |
| Where | `backend/payments/views.py`, `backend/accounts/superadmin_views.py`, `backend/anomalies/reports.py` |
| Issue | [LuisDulo/smart-school-feeding#114](https://github.com/LuisDulo/smart-school-feeding/issues/114) |
| Fix | [LuisDulo/smart-school-feeding#124](https://github.com/LuisDulo/smart-school-feeding/pull/124) |
| Status | Fixed |

## What was wrong

Several views passed query parameters straight to `int()`. Each of these returned a 500:

- `?months=abc` on the monthly report
- `?days=abc` on the balance trend
- `?days=abc` on the super admin analytics and reports, and the school reports
- `?meal_account_id=abc` on every endpoint that uses `resolve_meal_account`

The report endpoints also had no upper bound on `days`, so one request could ask for any window size.

None of this leaks data. With `DEBUG` off, a 500 shows no stack trace. But a crash on bad input means the input was never validated, and an unbounded window is a cheap way to load the database.

## Fix

- A small helper, `core.params.int_param`, returns a 400 for a value that is not a whole number and for one outside its range. Endpoints that already clamped (monthly report 1 to 12, balance trend 1 to 90) keep clamping.
- Report windows are limited to 1 to 365 days.
- `resolve_meal_account` treats a non-numeric id as not found, the same 404 as an id that belongs to someone else.

## Proof

`backend/tests/test_security_bad_parameters.py` covers 7 cases, all failing before the fix.
