# Implementation Plan

## Phase 1: Contract

- [x] Classify supported, lossy, and unsupported source-to-YAML mappings.
- [x] Specify deterministic handling for entities, roles, periods, enums,
  missing values, explicit zero, decimal money, and expected outputs.

## Phase 2: Diagnostics and examples

- [x] Add a machine-readable, fail-closed diagnostics schema.
- [x] Add lossless, warned-lossy, and unsupported examples.
- [x] Add focused schema and outcome-consistency tests.

## Phase 3: Verification

- [x] Review the guide against OpenFisca Core 44.x runner and simulation-builder
  behavior.
- [x] Run focused tests, style validation, and Conductor validation.
- [x] Record the boundary that future converter code requires a separately
  scoped consumer, issue, and tests.

## Phase 4: Hosted closeout

- [x] Open and review the fork pull request, recording its immutable head and
  hosted-check evidence.
- [x] Merge the pull request and close fork issue #3.
- [x] Record the merge commit, satisfy the issue gate, and archive the track.

> CHECKPOINT (2026-07-19): PR #16 passed focused validation and the complete
> OpenFisca Core pull-request matrix at head
> `ca396e6a0f8df35df1c7dc819843891a1a4a384e`, then merged as
> `4e18a4adc3c1e534e5f1763feefb278a67b14ff9`. GitHub closed fork issue #3.
> The evidence ledger preserves the implementation, immutable PR head, hosted
> runs, merge, and issue-close records. Track archived.
