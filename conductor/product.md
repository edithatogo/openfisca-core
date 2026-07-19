# Product Definition

OpenFisca Core is the Python computation engine and Web API foundation used by
OpenFisca country and extension packages.

## Users and Goals

- Policy model authors need deterministic, period-aware calculations.
- Integrators need stable Python and Web API contracts.
- Maintainers need reproducible tests, packaging, and release automation.

## Capabilities

- Variables, entities, holders, simulations, periods, parameters, and reforms.
- NumPy-backed computation with tracing and data-storage support.
- Optional Web API and packaging for pip and Conda environments.

## Non-goals

- Country-specific legislation and policy decisions.
- Runtime AI decisions.
- Treating fork-controlled CI as independent external validation.
