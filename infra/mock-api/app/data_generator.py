"""
Deterministic synthetic record generator.

Given a date and a global seed, this always produces the SAME set of
records, in the SAME order, with the SAME records flagged as malformed.
This determinism is deliberate: it means a learner's bug is reproducible,
and grading/test assertions can rely on fixed record counts and known
malformed positions instead of chasing randomness.

Re-seeding (via the RANDOM_SEED env var) gives a fresh dataset for
"make it break" exercises where staleness would hide the point.
"""

import hashlib
import os
import random
from datetime import date as date_type
from typing import Any

CUSTOMERS = [f"cust_{i:04d}" for i in range(1, 51)]
CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY"]
STATUSES = ["completed", "pending", "refunded", "failed"]

GLOBAL_SEED = int(os.environ.get("RANDOM_SEED", "42"))
RECORDS_PER_DAY = int(os.environ.get("RECORDS_PER_DAY", "537"))
MALFORMED_RATE = float(os.environ.get("MALFORMED_RATE", "0.03"))


def _date_seed(date_str: str) -> int:
    """Combine the global seed with the requested date so every date has
    its own stable-but-distinct dataset."""
    digest = hashlib.sha256(f"{GLOBAL_SEED}:{date_str}".encode()).hexdigest()
    return int(digest[:8], 16)


def _make_good_record(rng: random.Random, index: int, date_str: str) -> dict[str, Any]:
    external_id = f"txn_{date_str.replace('-', '')}_{index:06d}"
    return {
        "external_id": external_id,
        "customer_id": rng.choice(CUSTOMERS),
        "amount": round(rng.uniform(1.00, 4999.99), 2),
        "currency": rng.choice(CURRENCIES),
        "status": rng.choice(STATUSES),
        "source_created_at": f"{date_str}T{rng.randint(0,23):02d}:{rng.randint(0,59):02d}:{rng.randint(0,59):02d}Z",
        "source_updated_at": f"{date_str}T{rng.randint(0,23):02d}:{rng.randint(0,59):02d}:{rng.randint(0,59):02d}Z",
        "payload": {
            "channel": rng.choice(["web", "mobile", "pos", "api"]),
            "retry_count": rng.randint(0, 2),
        },
    }


def _corrupt(record: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Apply one deterministic-but-varied corruption to an otherwise good record."""
    corruption = rng.choice(
        ["missing_field", "wrong_type", "truncated", "null_required", "extra_junk"]
    )
    record = dict(record)  # shallow copy

    if corruption == "missing_field":
        field = rng.choice(["customer_id", "amount", "currency", "status"])
        del record[field]
    elif corruption == "wrong_type":
        record["amount"] = str(record["amount"]) + "USD"  # amount should be numeric
    elif corruption == "truncated":
        # Simulate a response cut off mid-record (common with flaky upstream APIs)
        return {"external_id": record["external_id"], "customer_id": record["customer_id"]}
    elif corruption == "null_required":
        record["external_id"] = None
    elif corruption == "extra_junk":
        record["__debug"] = {"internal_note": "should never reach prod"}
        record["status"] = "UNKNOWN_STATUS_CODE_7"

    return record


def generate_records_for_date(date_str: str) -> list[dict[str, Any]]:
    """Full, deterministic record set for a date, before pagination is applied."""
    # Validate date format early - the real API would do this too
    date_type.fromisoformat(date_str)

    seed = _date_seed(date_str)
    rng = random.Random(seed)

    records = []
    for i in range(RECORDS_PER_DAY):
        record = _make_good_record(rng, i, date_str)
        if rng.random() < MALFORMED_RATE:
            record = _corrupt(record, rng)
        records.append(record)

    return records
