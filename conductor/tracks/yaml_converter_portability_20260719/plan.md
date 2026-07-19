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
