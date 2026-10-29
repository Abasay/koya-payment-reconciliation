#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

# txn_id -> (parsed ts, line number, event); only the latest attempt is kept.
latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for n, line in enumerate(f):
        try:
            event = json.loads(line)
            txn_id = event.get("txn_id")
            ts = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        except (ValueError, AttributeError, KeyError, TypeError):
            continue
        if not txn_id:
            continue
        # Later ts wins; on an exact tie the later line in the file wins.
        if txn_id not in latest or (ts, n) >= latest[txn_id][:2]:
            latest[txn_id] = (ts, n, event)

total = Decimal(0)
count = 0
for _, _, event in latest.values():
    if event.get("status") == "success":
        amount = event["amount"]
        if isinstance(amount, str):
            amount = amount.replace(",", "").strip()
        total += Decimal(str(amount))
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{total.quantize(Decimal(1), rounding=ROUND_HALF_UP)}")
