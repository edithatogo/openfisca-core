# YAML Converter Portability and Loss Boundaries

## Overview

Complete fork issue [#3](https://github.com/edithatogo/openfisca-core/issues/3)
with a maintained contract for deterministic external-fixture adapters.

## Requirements

1. Classify entity, role, variable, period, enum, missing-value, explicit-zero,
   decimal/money, and expected-output mappings as lossless, lossy, or unsupported.
2. Require explicit, machine-readable diagnostics and fail-closed behavior.
3. Provide valid lossless, warned-lossy, and unsupported examples.
4. State target runtime, country-package, and semantic-equivalence boundaries.
5. Keep conversion deterministic and prohibit runtime AI decisions.

## Acceptance Criteria

- `docs/yaml-portability.md` defines the maintained mapping surface.
- A Draft 2020-12 schema enforces diagnostic structure and outcome consistency.
- Focused tests validate all examples and rejection cases.
- No generic converter or source-specific mapping is added without a separately
  scoped consumer and implementation issue.

## Out of Scope

- A universal converter, source schema, or country-package ontology.
- Silent coercion, inferred legal meaning, or runtime AI decisions.
- Claims of compatibility across unpinned country-package releases.
