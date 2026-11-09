# 05. Login response time reveals which emails have accounts

| | |
|---|---|
| Severity | Low |
| OWASP Top 10 (2021) | A07 Identification and Authentication Failures |
| Where | `backend/accounts/views.py` (`LoginView`) |
| Issue | [LuisDulo/smart-school-feeding#113](https://github.com/LuisDulo/smart-school-feeding/issues/113) |
| Fix | [LuisDulo/smart-school-feeding#123](https://github.com/LuisDulo/smart-school-feeding/pull/123) |
| Status | Fixed |

## What was wrong

Login already returned the same message, "Invalid email or password.", for an unknown email and for a wrong password. The timing was different, though:

- **Unknown email:** the view returned as soon as the database lookup failed.
- **Known email:** it first ran `bcrypt.checkpw`, which is deliberately slow.

By timing responses, an attacker can tell which emails have accounts. Those emails become targets for password guessing or phishing. The login rate limit (10 a minute) slows this down but does not stop it.

## Fix

When the email is unknown, the password is checked against a fixed dummy bcrypt hash, and the login always fails. Both paths now do one bcrypt check and return the same 401 body.

## Proof

`backend/tests/test_security_login_enumeration.py` wraps `bcrypt.checkpw`, logs in once with an unknown email and once with a known email, and checks for two calls and identical responses. Before the fix it saw one call.
