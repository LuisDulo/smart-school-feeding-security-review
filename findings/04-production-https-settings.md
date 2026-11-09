# 04. Production settings fail Django's deployment checklist

| | |
|---|---|
| Severity | Medium |
| OWASP Top 10 (2021) | A05 Security Misconfiguration, A02 Cryptographic Failures |
| Where | `backend/core/settings.py` |
| Issue | [LuisDulo/smart-school-feeding#112](https://github.com/LuisDulo/smart-school-feeding/issues/112) |
| Fix | [LuisDulo/smart-school-feeding#122](https://github.com/LuisDulo/smart-school-feeding/pull/122) |
| Status | Fixed |

## What was wrong

The settings already handled the basics:

- `SECRET_KEY` and `DEBUG` come from the environment.
- `DEBUG` defaults to off.
- CORS allows every origin only in debug.

Nothing in the settings forced HTTPS, though. With `DEBUG=False`, `python manage.py check --deploy` reported:

```
security.W004  SECURE_HSTS_SECONDS is not set
security.W008  SECURE_SSL_REDIRECT is not True
security.W012  SESSION_COOKIE_SECURE is not True
security.W016  CSRF_COOKIE_SECURE is not True
```

The API carries passwords, JWTs and payment data. Without the redirect and HSTS, one request over plain HTTP, for example a link typed without `https://`, sends those over the network unencrypted.

## Fix

When `DEBUG` is off:

- Redirect HTTP to HTTPS. Setting `SECURE_SSL_REDIRECT=False` turns this off for a trusted HTTP-only test setup.
- Send HSTS for one year, including subdomains, with preload.
- Make session and CSRF cookies secure-only. The admin site uses them.
- Trust `X-Forwarded-Proto` only when `NUM_PROXIES` is set. That is the case where a proxy terminating TLS sits in front and overwrites the header. Trusting the header without such a proxy would let a client claim it is on HTTPS.

## Proof

`backend/tests/test_security_deploy_settings.py` runs `manage.py check --deploy --fail-level WARNING` in a subprocess with production settings. It failed with the four warnings above and passes now. CI runs it on every push.
