# AI Guardrail Log

One entry per module. Each entry records what the AI assistant actually
did, what was caught (or confirmed clean), and the one-line rule adopted
going forward. This is not a list of failures — a module where a careful
review found nothing wrong is still worth an entry. The log itself is
the deliverable, not just the fixed code.

---

## Module 1 — Project structure, packaging, dependency management

**Task given to the assistant:** add a `validate` subcommand to the
`salesreport` CLI, checking a sales CSV for missing or malformed rows.

**What actually happened:** the assistant took a test-first approach —
wrote `tests/test_cli.py` with a regression test before implementing the
feature, which is good practice on its own. But two real issues turned
up in review:

1. **Un-diagnosed `sys.path.insert` hack.** The generated test file
   included `sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))`
   at the top — a manual patch to Python's import path. This was
   unnecessary: the package was already installed with `pip install -e .`
   inside an activated virtual environment, so the import should have
   worked without any path manipulation at all. The presence of this
   line pointed to the assistant working in a terminal session where the
   venv wasn't actually activated (`python: command not found` appeared
   in the same session), and papering over that with a path hack instead
   of surfacing the real problem.
2. **Duplicated file-reading logic.** The new `validate_sales_rows`
   function opened the file and ran `csv.DictReader` itself from
   scratch, instead of calling the already-existing `read_sales_rows`
   function sitting right above it in the same file. Two independent
   code paths now read a CSV the same way — a real duplication risk, not
   just a style nitpick.

**Guardrail adopted:** Before accepting any AI-generated test file,
check for manual `sys.path` manipulation — if it's there, it's usually a
sign the assistant is working around a broken environment (unactivated
venv, bad working directory) instead of the actual code being wrong.
Fix the environment, not the symptom. Separately: when an AI adds a new
function, check whether it duplicates logic that already exists
elsewhere in the same file before accepting the diff.

---

## Module 2 — Typing and code quality as a safety net

*(Fill in after completing Module 2's AI-assisted round.)*

---

## Module 3 — Error handling, retries, resilience

*(Fill in after completing Module 3's AI-assisted round.)*

---

## Module 4 — Idempotency and safe reprocessing

*(Fill in after completing Module 4's AI-assisted round.)*

---

## Module 5 — Testing data pipelines, not just functions

*(Fill in after completing Module 5's AI-assisted round.)*

---

## Module 6 — Logging, observability, debuggability

*(Fill in after completing Module 6's AI-assisted round.)*

---

## Module 7 — Concurrency, async, working at scale

*(Fill in after completing Module 7's AI-assisted round.)*

---

## Module 8 — Configuration, secrets, environments

*(Fill in after completing Module 8's AI-assisted round.)*

---

## Module 9 — Packaging for deployment, CI/CD

*(Fill in after completing Module 9's AI-assisted round.)*
