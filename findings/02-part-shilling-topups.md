# 02. Part-shilling top-ups are credited more than M-Pesa charged

| | |
|---|---|
| Severity | Medium |
| OWASP Top 10 (2021) | A04 Insecure Design |
| Where | `backend/payments/serializers.py`, `backend/payments/mpesa.py`, `backend/payments/views.py` |
| Issue | [LuisDulo/smart-school-feeding#110](https://github.com/LuisDulo/smart-school-feeding/issues/110) |
| Fix | [LuisDulo/smart-school-feeding#120](https://github.com/LuisDulo/smart-school-feeding/pull/120) |
| Status | Fixed |

## What was wrong

The two halves of a top-up disagreed about the amount:

- **Charging.** Amounts are stored in cents, but M-Pesa charges whole shillings. `stk_push` sends Daraja `max(1, amount_cents // 100)`.
- **Crediting.** The callback credits the full `amount_cents`.

The serializer accepted any amount of 100 cents or more. A top-up of 199 cents charged KES 1 and credited KES 1.99. With up to 99 cents gained per top-up, the loss is small, but money appeared that was never paid. The mobile app sent `Math.round(ksh * 100)` for amounts like 50.75.

There was a second gap in the same place. When Daraja rejected a push and returned no `CheckoutRequestID`, the pending transaction was saved with an empty reference. A callback carrying an empty id could then match it.

## Fix

- The serializer refuses amounts that are not a multiple of 100 cents.
- The mobile top-up screen only accepts whole shillings.
- When Daraja returns no `CheckoutRequestID`, the transaction is marked failed and the client gets a 502.
- After [01](01-forged-mpesa-callback.md), the callback also checks that `Amount` matches the shillings charged.

## Proof

`backend/tests/test_security_topup_amount.py`:

- a part-shilling amount is refused (failed before the fix)
- Daraja returning no checkout id fails the transaction (failed before the fix)
- a whole-shilling amount is accepted (the control, which passed both before and after)
