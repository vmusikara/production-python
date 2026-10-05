"""
Mock flaky third-party API for the "Production Python for Data Engineers" capstone.

Simulates the kind of unreliable upstream integration every data team has:
rate limiting, timeouts, occasional malformed records, and pagination —
including a couple of pagination edge cases (duplicate page, empty page)
that matter later for the idempotency module.

This is shared infrastructure, reused by Modules 3, 4, 6, and 7. It is
NOT part of the capstone code itself - learners treat it as an external
system they don't control, same as a real third-party API.
"""

import asyncio
import os
import time
from collections import deque

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse

from .data_generator import generate_records_for_date

app = FastAPI(title="Mock Flaky Ingestion API", version="1.0.0")

# ---- Configuration (env-driven, see .env.example) --------------------------

PAGE_SIZE = int(os.environ.get("PAGE_SIZE", "50"))

RATE_LIMIT_MAX_REQUESTS = int(os.environ.get("RATE_LIMIT_MAX_REQUESTS", "10"))
RATE_LIMIT_WINDOW_SECONDS = float(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "10"))

TIMEOUT_RATE = float(os.environ.get("TIMEOUT_RATE", "0.05"))  # fraction of requests that hang
TIMEOUT_HANG_SECONDS = float(os.environ.get("TIMEOUT_HANG_SECONDS", "12"))

# Pagination chaos: which page number (1-indexed, per date) gets duplicated
# or returned empty. Set to 0 to disable. Deterministic on purpose.
DUPLICATE_PAGE_NUMBER = int(os.environ.get("DUPLICATE_PAGE_NUMBER", "3"))
EMPTY_PAGE_NUMBER = int(os.environ.get("EMPTY_PAGE_NUMBER", "0"))  # 0 = disabled by default

# ---- In-memory rate limiter (global, simple sliding window) -----------------
# Real APIs rate-limit per API key; this one is global for simplicity since
# the course only ever runs one learner against it at a time locally.

_request_timestamps: deque[float] = deque()


def _check_rate_limit() -> None:
    now = time.monotonic()
    while _request_timestamps and now - _request_timestamps[0] > RATE_LIMIT_WINDOW_SECONDS:
        _request_timestamps.popleft()

    if len(_request_timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        retry_after = RATE_LIMIT_WINDOW_SECONDS - (now - _request_timestamps[0])
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Slow down.",
            headers={"Retry-After": str(max(1, round(retry_after)))},
        )

    _request_timestamps.append(now)


# ---- Deterministic-but-seeded "should this request misbehave" check --------

def _should_hang(date_str: str, page: int) -> bool:
    """Deterministic per (date, page) so a learner can reproduce a specific
    timeout without waiting on true randomness, but it still varies across
    pages/dates so it's not trivially predictable from the outside."""
    import hashlib

    digest = hashlib.sha256(f"timeout:{date_str}:{page}".encode()).hexdigest()
    bucket = int(digest[:4], 16) / 0xFFFF
    return bucket < TIMEOUT_RATE


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/records")
async def get_records(
    request: Request,
    date: str = Query(..., description="Date to fetch records for, YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    force_429: bool = Query(False, description="Lab override: force a rate-limit response"),
    force_timeout: bool = Query(False, description="Lab override: force a hang"),
    chaos: bool = Query(True, description="Set false to disable all flakiness (pagination still works)"),
) -> Response:
    # --- Lab overrides, so learners can trigger a specific failure on demand
    # instead of waiting for it to occur naturally during a "make it break" drill.
    if force_429:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Slow down.",
            headers={"Retry-After": "5"},
        )
    if force_timeout:
        await asyncio.sleep(TIMEOUT_HANG_SECONDS)

    if chaos:
        _check_rate_limit()
        if _should_hang(date, page):
            await asyncio.sleep(TIMEOUT_HANG_SECONDS)

    try:
        all_records = generate_records_for_date(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD")

    total_records = len(all_records)
    total_pages = max(1, (total_records + PAGE_SIZE - 1) // PAGE_SIZE)

    if page > total_pages:
        raise HTTPException(status_code=404, detail=f"page {page} does not exist for {date}")

    # --- Pagination edge cases, only active when chaos=True ------------------
    effective_page = page
    if chaos and EMPTY_PAGE_NUMBER and page == EMPTY_PAGE_NUMBER:
        page_records: list = []
    elif chaos and DUPLICATE_PAGE_NUMBER and page == DUPLICATE_PAGE_NUMBER:
        # Serve the PREVIOUS page's content again, simulating an upstream bug
        # where a retried request replays a page instead of advancing.
        effective_page = max(1, page - 1)
        start = (effective_page - 1) * PAGE_SIZE
        page_records = all_records[start : start + PAGE_SIZE]
    else:
        start = (page - 1) * PAGE_SIZE
        page_records = all_records[start : start + PAGE_SIZE]

    has_more = page < total_pages

    return JSONResponse(
        {
            "date": date,
            "page": page,
            "page_size": PAGE_SIZE,
            "total_pages": total_pages,
            "total_records": total_records,
            "has_more": has_more,
            "next_page": page + 1 if has_more else None,
            "records": page_records,
        }
    )
