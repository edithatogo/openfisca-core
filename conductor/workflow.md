# Project Workflow

## Principles

1. `plan.md` is the task source of truth.
2. Use test-driven development for behavior changes and deterministic validation
   for governance-only changes.
3. Preserve unrelated changes and commit only owned paths.
4. Keep repository completion separate from publication, deployment, upstream
   acceptance, and independent review.

## Task Workflow

1. Select the next unblocked task and mark it in progress.
2. Define evidence, implement the smallest coherent change, and run targeted
   then complete applicable checks.
3. Review correctness, scope, security, public contracts, and provenance.
4. Commit one focused logical unit and record its revision and evidence.

## Project Commands

```text
environment: make install-deps install-edit install-test
targeted tests: pytest <applicable test paths>
full tests: make test
format check: make check-style
lint: make check-style
type check: make check-types
Conductor validation: python3 <bundled-validator> --root . --mode full --json
complete project gate: make test
```

Governance-only Conductor changes may use the bundled Conductor validator as
their complete gate because they do not alter runtime code or dependencies.

## Evidence and Completion

- Use `evidence.jsonl` schema 1.0 as each track's authoritative ledger.
- Evidence entries are append-only and hash-chained.
- Git notes are disabled.
- A completed retrospective track must cite its issue, merged PR, PR head SHA,
  merge commit, and all applicable hosted checks.
- Controlled-fork CI proves reproducibility in that environment, not independent
  validation or upstream acceptance.
- Isolation mode: off.

A task is complete only when its acceptance criteria, validation, metadata,
registry state, and remaining external boundaries agree.
