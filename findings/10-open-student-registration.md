# 10. Anyone can self-register as a student at any school

| | |
|---|---|
| Severity | Medium |
| OWASP Top 10 (2021) | A01 Broken Access Control, A04 Insecure Design |
| Where | `backend/accounts/serializers.py` (`RegisterSerializer`), `mobile/src/screens/RegisterScreen.js` |
| Issue | [LuisDulo/smart-school-feeding#118](https://github.com/LuisDulo/smart-school-feeding/issues/118) |
| Status | Open, waiting on a product decision |

## What is wrong

`POST /api/auth/register/` is public and accepts `role: "student"` with any `school_id`. The list of schools is public too, at `/api/auth/schools/`. Earlier work already stopped people from registering themselves as admin, bursar or kitchen staff (see `tests/test_security_registration.py`). Student accounts were left open on purpose, so that students can sign up from the mobile app.

The result is that anyone on the internet can add students to any school's roster. A script could add thousands. Those accounts:

- appear in the school admin's student list and in the dashboard's student count
- count toward the enrolment the meal demand forecast uses, so they inflate how much food the kitchen is told to prepare
- get a QR code the kitchen scanner accepts

They cannot actually be served a meal, because their balance is zero and they have no approved credit. So this is a data-integrity and forecasting problem, not a way to get free food.

## Why it is not fixed yet

Fixing it changes how students get accounts, which is a product decision, not a code bug:

- **Option A: remove student self-registration.** Students would be created only by admins, which `AdminCreateStudentView` already supports, and would log in with the details the school gives them. This is the simplest and safest option.
- **Option B: keep self-registration, but start students as pending.** A pending student would not appear in counts or forecasts until a school admin approves them. This needs a new status field and an approval screen.

Either way, the rate limit on registration (20 an hour per IP) stays as a backstop.
