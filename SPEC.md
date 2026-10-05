# Capstone Spec: Production-Grade Ingestion & Transformation Service

This is the spec assigned in full in Module 0. It doesn't change as you go —
every module adds one capability toward this same spec. If you ever lose
track of "what am I actually building," this file is the answer.

## Scenario

You're the data engineer responsible for pulling records from an unreliable,
paginated, rate-limited third-party API (the `mock-api` service running
alongside this repo) and landing them, correctly and safely, in a Postgres
warehouse table.

## Functional requirement

Ingest all records from the mock API for a given date, validate and
transform them, and upsert them into the `warehouse.records` Postgres table.

**Must be safely re-runnable and safely resumable from partial failure** —
running the pipeline twice, or restarting it mid-run, must never duplicate
or corrupt data.

## Non-functional requirements (the actual grading rubric)

Each line below is delivered by a specific module. Don't try to do these
out of order — later modules assume earlier ones are in place.

- [ ] Installable package with a CLI entry point — **Module 1**
- [ ] Fully typed (`mypy --strict` passing), pydantic models at every data boundary — **Module 2**
- [ ] Classified exception hierarchy, backoff-and-jitter retries, dead-letter path for unrecoverable records — **Module 3**
- [ ] Provably idempotent — a test that runs the pipeline twice and asserts identical end state — **Module 4**
- [ ] Unit, integration, and property-based test coverage, including failure paths — **Module 5**
- [ ] Structured logs with a run ID, sufficient to diagnose any failure without rereading code or rerunning — **Module 6**
- [ ] Bounded-concurrency async fetch with measured before/after performance, plus at least one chunked/generator-based transform — **Module 7**
- [ ] Typed, validated, environment-aware configuration with no secrets in code — **Module 8**
- [ ] CI pipeline gating merges (lint, type-check, test) and building a container image — **Module 9**
- [ ] An **AI guardrail log** (`AI_GUARDRAIL_LOG.md`, at the root of this repo) — one line per module noting the AI failure pattern caught (if any) and the guardrail adopted — **built incrementally, Modules 1-9**

## Final deliverable (capstone week)

A short (5-7 minute) recorded walkthrough where you explain three of your
own design decisions out loud and defend them, **plus one moment where you
caught and fixed an AI-generated mistake.** This doubles as interview
rehearsal, not just a project demo.

## Infrastructure you're given (don't rebuild this — it's provided)

- `mock-api` — the flaky third-party API. Rate-limits, times out, occasionally
  returns malformed records, and paginates. Treat it exactly like a real
  external API you don't control: read its behavior, don't read its source.
- `postgres` — your warehouse database, schema pre-applied (see
  `infra/postgres/init.sql`).
- Both are started with `docker compose up` — see `README.md` and
  `SETUP.md` if this is your first time.

## Ground rule: capstone vs. interview drills

Your capstone code stays your capstone code. Interview drills (recall,
judgment, debugging, AI-review questions in each module) always use
scenarios and code you've never seen before — never this repo. Don't mix
the two. If a drill ever seems to reference your own capstone code, that's
a mistake in the drill, not a hint to reuse your solution.
