# 08. Dashboard and mobile dependencies with known vulnerabilities

| | |
|---|---|
| Severity | Medium |
| OWASP Top 10 (2021) | A06 Vulnerable and Outdated Components |
| Where | `dashboard/package-lock.json`, `mobile/package-lock.json` |
| Issue | [LuisDulo/smart-school-feeding#116](https://github.com/LuisDulo/smart-school-feeding/issues/116) |
| Fix | [LuisDulo/smart-school-feeding#126](https://github.com/LuisDulo/smart-school-feeding/pull/126) |
| Status | Fixed where it ships to users; build tooling remains |

## What was wrong

`npm audit --omit=dev` before the fix:

| App | Total | Critical | High | Moderate | Low |
|---|---|---|---|---|---|
| dashboard | 45 | 2 | 19 | 8 | 16 |
| mobile | 18 | 1 | 9 | 7 | 1 |

Full lists: [evidence/npm-audit-dashboard-before.txt](../evidence/npm-audit-dashboard-before.txt) and [evidence/npm-audit-mobile-before.txt](../evidence/npm-audit-mobile-before.txt).

Most of these were in build and development tooling, which never reaches a user's browser or phone. The one that mattered at runtime was `follow-redirects`. It is used by axios, which both apps use for every API call, and could forward credentials across origins on a redirect.

## Fix

`npm audit fix` without `--force`. Only the lockfiles changed, and every package stayed inside the ranges in `package.json`.

| App | After | Critical | High | Moderate | Low |
|---|---|---|---|---|---|
| dashboard | 36 | 0 | 13 | 7 | 16 |
| mobile | 4 | 0 | 0 | 4 | 0 |

Both apps were checked after the change. The dashboard builds with `npm run build`. For mobile, a clean `npm ci` from the new lockfile followed by `expo export --platform android` succeeds.

## What remains, and why

- **Dashboard.** Everything left comes in through `react-scripts`: jest, webpack and its dev server, svgo, workbox and postcss. These run on the developer's machine while building and are not in the built bundle. The only automatic fix, `npm audit fix --force`, would install `react-scripts@0.0.0` and break the build. The real fix is to move off Create React App, which is no longer maintained, to Vite.
- **Mobile.** The four moderates are `glob` and `minimatch` inside Expo's config tooling, which also runs only at build time.

CI fails on any critical advisory in either app ([11](11-no-ci.md)).
