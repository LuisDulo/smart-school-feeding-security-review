# 09. Payer phone numbers written to the logs

| | |
|---|---|
| Severity | Low |
| OWASP Top 10 (2021) | A09 Security Logging and Monitoring Failures |
| Where | `backend/payments/views.py` (`mpesa_callback`) |
| Issue | Part of [LuisDulo/smart-school-feeding#109](https://github.com/LuisDulo/smart-school-feeding/issues/109) |
| Fix | [LuisDulo/smart-school-feeding#119](https://github.com/LuisDulo/smart-school-feeding/pull/119) |
| Status | Fixed |

## What was wrong

The callback logged every payload in full:

```python
logger.info(f"Daraja callback received: {payload}")
```

A successful Daraja payload includes the payer's phone number. Logs are kept longer, copied more widely and protected less than the database. Kenya's Data Protection Act 2019 treats a phone number as personal data, so the logs held personal data with no reason to.

## Fix

The log line now records only the `CheckoutRequestID` and the result code. The full payload is still stored on the transaction (`callback_payload`) for the audit trail, where database access controls apply.

## Proof

`test_phone_number_is_not_logged` in `backend/tests/test_security_mpesa_callback.py` captures the `payments` logger during a genuine callback and checks that the number does not appear.
