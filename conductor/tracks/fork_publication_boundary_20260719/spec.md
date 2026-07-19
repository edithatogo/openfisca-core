# Specification

## Objective

Prevent controlled forks from attempting publication with upstream credentials
while preserving canonical OpenFisca release behavior and all validation jobs.

## Contract

- `publish-to-pypi` runs only when `github.repository` is
  `openfisca/openfisca-core` and functional changes are present.
- Dependent Conda publication and release jobs skip naturally on controlled
  forks.
- Pull-request validation is unchanged.
- No credential is copied, invented, or made optional on the canonical repo.

## Acceptance

- Fork post-merge runs complete without an attempted publication.
- Canonical-repository publication conditions retain their existing behavior.
- Hosted pull-request checks pass before merge.
