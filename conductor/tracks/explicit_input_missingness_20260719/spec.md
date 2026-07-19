# Explicit-input Missingness Retrospective

## Overview

Record the completed fork-local work from issue
[`#2`](https://github.com/edithatogo/openfisca-core/issues/2) and merged PR
[`#4`](https://github.com/edithatogo/openfisca-core/pull/4) as a durable
Conductor track.

## Requirements

1. Distinguish periods explicitly written through `Holder.set_input` from
   default and formula-calculated values without changing calculation semantics.
2. Expose holder and simulation queries for explicit-input state.
3. Preserve provenance through period casting, deletion, and clone isolation.
4. Record the merged implementation and complete applicable hosted PR evidence.

## Acceptance Criteria

- `Holder.is_input` and `Holder.get_value_state` report explicit/default state.
- Equivalent simulation helpers exist.
- Focused regressions cover explicit zero, omission, formula cache, period
  casting, deletion, eternal variables, and clone isolation.
- PR `#4` is merged at `cb677211039ce0d1ad4cb96fa82750dc20ff0e88`.
- All 25 applicable PR-head hosted checks are recorded with job URLs.

## Authoritative Inputs

- Fork issue `#2`, fork PR `#4`, PR head
  `2625bec42814901b331164fe2b014ff33149dc7d`, and merge commit
  `cb677211039ce0d1ad4cb96fa82750dc20ff0e88`.
- Runtime implementation and tests at the merge commit.

## Evidence Boundary

The hosted checks ran in the controlled fork. They are first-party operational
evidence, not independent validation and not evidence of upstream acceptance.
Post-merge publishing is outside this retrospective acceptance contract.

## Out of Scope

- Any upstream change, submission, or acceptance claim.
- New runtime behavior beyond merged PR `#4`.
