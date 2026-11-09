# Smart School Feeding: security review

A security review of [smart-school-feeding](https://github.com/LuisDulo/smart-school-feeding), my school meal payment system:

- a Django REST API
- a React dashboard for school staff
- a React Native (Expo) app for parents, students and kitchen staff
- M-Pesa top-ups through Safaricom's Daraja API

Parents put real money on a child's meal account, so the review starts from the money and works outward.

Every finding was proved with a test that failed before the fix and passes after it. Each fix went through its own issue and pull request in the app's repository. The review also added CI, so tests and security scans now run on every change.

## Summary

| # | Finding | Severity | OWASP 2021 | Status |
|---|---|---|---|---|
| [01](findings/01-forged-mpesa-callback.md) | Forged M-Pesa callbacks credit a meal account without payment | Critical | A08 | Fixed in [LuisDulo/smart-school-feeding#119](https://github.com/LuisDulo/smart-school-feeding/pull/119) |
| [07](findings/07-vulnerable-python-dependencies.md) | Python dependencies with 49 known vulnerabilities | High | A06 | Fixed in [LuisDulo/smart-school-feeding#125](https://github.com/LuisDulo/smart-school-feeding/pull/125) |
| [02](findings/02-part-shilling-topups.md) | Part-shilling top-ups credited more than M-Pesa charged | Medium | A04 | Fixed in [LuisDulo/smart-school-feeding#120](https://github.com/LuisDulo/smart-school-feeding/pull/120) |
| [03](findings/03-long-lived-access-tokens.md) | Access tokens last 12 hours and survive logout | Medium | A07 | Fixed in [LuisDulo/smart-school-feeding#121](https://github.com/LuisDulo/smart-school-feeding/pull/121) |
| [04](findings/04-production-https-settings.md) | Production settings fail Django's deployment checklist | Medium | A05 | Fixed in [LuisDulo/smart-school-feeding#122](https://github.com/LuisDulo/smart-school-feeding/pull/122) |
| [08](findings/08-vulnerable-javascript-dependencies.md) | Dashboard and mobile dependencies with known vulnerabilities | Medium | A06 | Fixed in [LuisDulo/smart-school-feeding#126](https://github.com/LuisDulo/smart-school-feeding/pull/126), build tooling remains |
| [10](findings/10-open-student-registration.md) | Anyone can self-register as a student at any school | Medium | A01 | Open, needs a product decision ([LuisDulo/smart-school-feeding#118](https://github.com/LuisDulo/smart-school-feeding/issues/118)) |
| [05](findings/05-login-account-enumeration.md) | Login timing reveals which emails have accounts | Low | A07 | Fixed in [LuisDulo/smart-school-feeding#123](https://github.com/LuisDulo/smart-school-feeding/pull/123) |
| [06](findings/06-malformed-parameters.md) | Malformed query parameters crash endpoints | Low | A04 | Fixed in [LuisDulo/smart-school-feeding#124](https://github.com/LuisDulo/smart-school-feeding/pull/124) |
| [09](findings/09-phone-numbers-in-logs.md) | Payer phone numbers written to the logs | Low | A09 | Fixed in [LuisDulo/smart-school-feeding#119](https://github.com/LuisDulo/smart-school-feeding/pull/119) |
| [11](findings/11-no-ci.md) | No CI, so nothing stopped a fixed bug from returning | Process | A05 | Fixed in [LuisDulo/smart-school-feeding#127](https://github.com/LuisDulo/smart-school-feeding/pull/127) |

Severity is my judgement of impact and how easy the issue is to exploit in this app:

- **Critical:** anyone with an account can steal money or meals.
- **High:** reachable without an account, or affects every request.
- **Medium:** needs a stolen token, a misconfiguration or a scripted attack.
- **Low:** leaks little, or only makes an attack slightly easier.

## Scope

The review covered smart-school-feeding at commit `ccda265` (9 November 2026):

- `backend/`, about 6,400 lines of Python excluding migrations
- the API clients and auth code in `dashboard/` and `mobile/`
- each app's dependencies
- the repository's full git history

Not covered:

- **Live deployment.** There is no live deployment yet, so there was no dynamic scan (for example OWASP ZAP) against a real server, and no review of hosting, TLS certificates or the reverse proxy.
- **Daraja's side.** Safaricom's behaviour was taken from its documentation.
- **Device security.** No testing of rooted phones or extraction of the mobile app's stored data.

## Method

1. **Inventory.** Read every URL route and view, and mapped each one to its authentication, its permission class and how it limits queries to the user's own school or child.
2. **Manual review against the OWASP Top 10.** The money flow came first: initiating a top-up, the M-Pesa callback, and credit requests. Then authentication, JWT handling, access control between schools and roles, input handling and settings.
3. **Automated scans:**
   - pip-audit on the backend's installed packages
   - bandit on the backend source
   - `npm audit --omit=dev` on both JavaScript apps
   - a search of every commit in the git history for keys, passwords and private keys
4. **Proof.** For each finding, a test that describes the safe behaviour, run against the unfixed code to show it fails. Before any fix, 20 of the new tests failed. The one control test, a valid top-up, passed.
5. **Fix.** One issue, branch and pull request per finding, merged into the app's main branch with the full suite passing (244 tests).

The raw scan output is in [evidence/](evidence/).

## What held up

Several areas were checked and found sound. Most of them were hardened in earlier sprints.

- **Isolation between schools.** Every staff endpoint limits its queries to `request.user.school`:
  - students, menu items and combos
  - meal logs, flags and credit requests
  - support issues, reports and forecasts

  Asking for another school's object returns 404, not 403, so ids cannot be probed. `tests/test_school_isolation.py` covers this.
- **Parent and child access.** Parents reach only their linked children through `resolve_meal_account`. Payment status checks the caller is the student, a guardian or same-school staff, and returns 404 otherwise.
- **Roles.**
  - Public registration cannot create admin, bursar or kitchen accounts.
  - Only admins approve credit.
  - Only the super admin sees data across schools.
- **Passwords:**
  - bcrypt hashing
  - Django's password validators on every account-creation path
  - generic login errors
  - a login rate limit of 10 a minute, plus limits on registration and refresh
- **Refresh tokens.** They rotate, the old one is blacklisted, and logout revokes the current one.
- **Injection.** All database access goes through the Django ORM. There is no `raw()`, `extra()` or cursor SQL, and nothing builds shell commands or templates from user input.
- **Secrets:**
  - `SECRET_KEY` and the Daraja credentials come from the environment, and the app will not start without `SECRET_KEY`
  - the git history holds no real keys or passwords, only `.env.example` placeholders and test-fixture passwords
  - Firebase key files are ignored by git
- **Static analysis.** bandit found nothing of medium or high severity. All 59 low findings are `random` used for demo data, plus one deliberate `try/except/pass` in forecasting.

## Recommendations

These are not fixed in this review:

1. **Decide on student registration** ([10](findings/10-open-student-registration.md)). Removing self-registration is the simplest fix.
2. **Confirm payments with Daraja before crediting.** The callback could call the STK Push query API, which `MPesaService.query_stk_status` already wraps. Then even a leaked callback URL could not credit a payment. Also allow callbacks only from Safaricom's IP ranges at the proxy.
3. **Store mobile tokens in the device keychain.** `expo-secure-store` keeps them in the Android Keystore or iOS Keychain instead of `AsyncStorage`.
4. **Move the dashboard's refresh token out of `localStorage`,** where any cross-site scripting bug could read it, into an `HttpOnly`, `SameSite=Strict` cookie.
5. **Replace `react-scripts`** (Create React App is no longer maintained) with Vite. That clears the 13 high-severity advisories left in the dashboard's build tooling ([08](findings/08-vulnerable-javascript-dependencies.md)).
6. **Run a dynamic scan** (OWASP ZAP baseline) against the first real deployment, and repeat `check --deploy` there.

## Reproducing

The proof tests live in the app's repository:

```bash
git clone https://github.com/LuisDulo/smart-school-feeding
cd smart-school-feeding/backend
pip install -r requirements.txt
python -m pytest tests/test_security_*.py
```

To see them fail, check out `ccda265` (the commit reviewed), copy the new test files in, and run them again. [poc/forge_callback.py](poc/forge_callback.py) shows finding 01 against a local development server.
