-- Warehouse schema for the "Production-Grade Ingestion & Transformation Service" capstone.
-- This runs automatically the first time the postgres container starts (via
-- docker-entrypoint-initdb.d). It only defines the TABLES the capstone writes
-- into -- it deliberately does NOT solve any module's actual logic (that's
-- the learner's job, module by module).

CREATE SCHEMA IF NOT EXISTS warehouse;

-- The destination table for validated, transformed records.
-- external_id is the natural key from the upstream API and is what Module 4's
-- idempotent upsert logic will key off of.
CREATE TABLE IF NOT EXISTS warehouse.records (
    external_id       TEXT PRIMARY KEY,
    customer_id       TEXT NOT NULL,
    amount            NUMERIC(12, 2) NOT NULL,
    currency          TEXT NOT NULL,
    status            TEXT NOT NULL,
    payload           JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_created_at TIMESTAMPTZ NOT NULL,
    source_updated_at TIMESTAMPTZ NOT NULL,
    ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Records that failed validation/transformation and couldn't be written to
-- warehouse.records. This is the dead-letter path introduced in Module 3.
CREATE TABLE IF NOT EXISTS warehouse.dead_letter (
    id            SERIAL PRIMARY KEY,
    external_id   TEXT,
    raw_payload   JSONB NOT NULL,
    error_reason  TEXT NOT NULL,
    failed_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Tracks each ingestion run so a restarted/re-run job can tell what it already
-- completed. This is scaffolding for Module 4 (idempotency/resumability) --
-- the learner designs how it's actually used, this just gives them a place
-- to persist run state instead of having to invent the table too.
CREATE TABLE IF NOT EXISTS warehouse.ingestion_runs (
    run_id               UUID PRIMARY KEY,
    ingestion_date       DATE NOT NULL,
    started_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at         TIMESTAMPTZ,
    status               TEXT NOT NULL DEFAULT 'running',  -- running | completed | failed
    last_successful_page INTEGER
);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_date ON warehouse.ingestion_runs (ingestion_date);
