# 01. Forged M-Pesa callbacks credit a meal account without payment

| | |
|---|---|
| Severity | Critical |
| OWASP Top 10 (2021) | A08 Software and Data Integrity Failures |
| Where | `backend/payments/views.py` (`mpesa_callback`), `backend/payments/urls.py` |
| Issue | [LuisDulo/smart-school-feeding#109](https://github.com/LuisDulo/smart-school-feeding/issues/109) |
| Fix | [LuisDulo/smart-school-feeding#119](https://github.com/LuisDulo/smart-school-feeding/pull/119) |
| Status | Fixed |

## What was wrong

Daraja reports the result of an STK Push by POSTing to a callback URL. Daraja sends no credentials and does not sign the request, so the app has to decide on its own whether a callback is genuine.

The callback at `/api/payments/callback/`:

- was public and exempt from CSRF, with no secret of any kind
- found the pending transaction by `CheckoutRequestID` and, if `ResultCode` was 0, added `tx.amount_cents` to the balance
- did not look at the `Amount` or `MpesaReceiptNumber` in the payload

The `CheckoutRequestID` is not secret either: `POST /api/payments/initiate/` returns it to the client.

## How it is exploited

1. Log in as any parent or student and start a top-up of KES 10,000, the maximum.
2. Ignore the PIN prompt on the phone. The response already contains `checkout_request_id`.
3. POST a success for that id to `/api/payments/callback/`:

```json
{"Body": {"stkCallback": {"CheckoutRequestID": "<id from step 2>", "ResultCode": 0}}}
```

The balance goes up by KES 10,000, and the parent gets a "Top-up received" push notification. Nothing was paid. Repeat as often as you like.

The existing test `test_confirmed_callback_updates_balance` did exactly this and passed. [poc/forge_callback.py](../poc/forge_callback.py) does it against a local development server.

## Fix

- The callback only answers at `/api/payments/callback/<DARAJA_CALLBACK_TOKEN>/`. The token is a random secret from the environment, compared with `hmac.compare_digest`. Any other path gets a 404, and so does every path while no token is set, so the endpoint fails closed. `MPesaService` appends the token to `DARAJA_CALLBACK_URL`, so only the server and Daraja know the full URL.
- A success is credited only if `Amount` equals the whole shillings that were charged and `MpesaReceiptNumber` is present and has not been credited before. Otherwise the transaction is marked failed and a warning is logged.
- A new `mpesa_receipt` column has a partial unique constraint, so the database refuses a second credit for the same receipt even under a race.
- Logs carry the `CheckoutRequestID` and result code, not the payload with the payer's phone number (see [09](09-phone-numbers-in-logs.md)).

## Proof

`backend/tests/test_security_mpesa_callback.py`, 8 tests, all failing before the fix:

- the old public URL is refused
- a wrong token is refused
- with no token configured, every callback is refused
- an amount that does not match the charge is not credited
- a success without a receipt is not credited
- a receipt can only be credited once
- a genuine callback is credited and its receipt is stored
- the phone number is not logged

## Further hardening

The secret URL stops forgery by anyone who does not know it. Two further steps would stop forgery even if the URL leaked:

- **Confirm with Daraja.** Before crediting, call the STK Push query API (`MPesaService.query_stk_status`, which already exists) and check that Daraja itself reports the payment as complete.
- **Allow only Safaricom's addresses.** At the reverse proxy, accept callbacks only from Safaricom's published callback IP ranges.
