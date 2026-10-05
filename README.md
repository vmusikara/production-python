# Production Python for Data Engineers — Capstone Starter Repo

This is the starter repo for the course capstone: **Production-Grade
Ingestion & Transformation Service**. Full spec is in [`SPEC.md`](./SPEC.md).

## First time here?

Follow [`SETUP.md`](./SETUP.md) first. It walks through installing Docker
and VS Code from scratch (Windows and Mac), step by step. Don't skip it even
if you think you already have Docker — the setup verification steps at the
end are quick and will save you a confusing debugging session three modules
from now.

## Getting this repo

You've been given these files as a **zip**, not a git clone URL. Extract
it and turn it into **your own GitHub repository** — full step-by-step
instructions (including how to do this correctly on Windows/WSL2) are in
`SETUP.md`, Part D. This matters because your capstone commits, module by
module, go into this same repo across the whole course — it's the artifact
you'll point to in interviews.

## Quick start (once Docker + VS Code are installed and verified)

```bash
# 1. Copy the environment file (never commit the real .env)
cp .env.example .env

# 2. Start the mock API and Postgres
docker compose up -d

# 3. Confirm both are healthy
docker compose ps
```

You should see both `pp4de_mock_api` and `pp4de_postgres` listed as
`healthy`. Then confirm the mock API responds:

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl "http://localhost:8000/records?date=2026-07-01&page=1"
# a page of JSON records
```

If either of those doesn't work, see the troubleshooting section in
`SETUP.md`.

## Repo layout

```
.
├── SPEC.md                  # the full capstone spec — read this next
├── SETUP.md                 # Docker + VS Code install, step by step
├── docker-compose.yml       # brings up mock-api + postgres
├── .env.example             # copy to .env, never commit .env itself
├── infra/
│   ├── mock-api/            # the flaky third-party API (provided, don't edit)
│   │   ├── app/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── postgres/
│       └── init.sql         # warehouse schema, applied automatically
└── (your capstone code goes here, starting in Module 1)
```

Everything under `infra/` is provided infrastructure — you read it to
understand how the mock API behaves (it's meant to be treated like a real
third-party API you don't control), but you don't need to modify it. Your
own capstone code starts accumulating in this repo from Module 1 onward.

## What's next

Head to Module 0 for the full capstone brief and the AI closed-loop
teaching content, then start Module 1.
