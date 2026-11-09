# 03. Access tokens last 12 hours and survive logout

| | |
|---|---|
| Severity | Medium |
| OWASP Top 10 (2021) | A07 Identification and Authentication Failures |
| Where | `backend/core/settings.py` (`SIMPLE_JWT`), `dashboard/src/services/api.js`, `mobile/src/services/api.js` |
| Issue | [LuisDulo/smart-school-feeding#111](https://github.com/LuisDulo/smart-school-feeding/issues/111) |
| Fix | [LuisDulo/smart-school-feeding#121](https://github.com/LuisDulo/smart-school-feeding/pull/121) |
| Status | Fixed |

## What was wrong

The API uses JWTs: a short access token on every request and a longer refresh token to get new ones. Logout blacklists the refresh token. Access tokens are stateless, though, so they cannot be revoked.

`ACCESS_TOKEN_LIFETIME` was 12 hours. A token taken from a shared school computer, a log, or the dashboard's `localStorage` worked for up to 12 hours, even after the user logged out or an admin changed their access.

Shortening the lifetime on the server alone would have logged everyone out every few minutes, because neither client used the refresh endpoint. Both called `/auth/token/refresh/` nowhere, and the dashboard cleared the session on the first 401.

## Fix

- **Server.** `ACCESS_TOKEN_LIFETIME` is now 15 minutes. Refresh tokens stay at 7 days, rotated, with the used one blacklisted, as hardened earlier in issue 42.
- **Retry on 401.** Both clients now handle a 401 by exchanging the refresh token once and retrying the request.
- **Parallel requests.** A rotated refresh token can be used only once, so parallel 401s share a single refresh call. Without that, the second refresh would fail and log the user out.
- **Expired sessions.** If the refresh fails, the session is over. The dashboard returns to the login page, and the mobile app logs out through its `AuthContext`.
- **Report download.** The mobile report download bypasses axios, so it makes one API call first, which refreshes the token if needed.

## Proof

- `backend/tests/test_security_token_lifetime.py` failed before the fix.
- The dashboard interceptor was run in Node against a stubbed server. Three parallel requests that all got a 401 caused one refresh and three successful retries. A spent refresh token cleared storage and redirected to the login page.

## Remaining risk

Tokens are still kept in `localStorage` (dashboard) and `AsyncStorage` (mobile). See [recommendations](../README.md#recommendations).
