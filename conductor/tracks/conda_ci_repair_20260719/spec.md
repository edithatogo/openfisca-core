# Conda CI Repair Retrospective

## Overview

Record the completed fork-local repair from issue
[`#9`](https://github.com/edithatogo/openfisca-core/issues/9) and merged PR
[`#10`](https://github.com/edithatogo/openfisca-core/pull/10) as a durable
Conductor track.

## Requirements

1. Replace the removed `conda mambabuild` path with a supported Conda build.
2. Preserve newer `rattler-build` recipe handling and make cache identity track
   workflow changes.
3. Support version checks in a tagless fork.
4. Record the merged repair and complete applicable hosted PR evidence.

## Acceptance Criteria

- The core Conda recipe no longer invokes `mambabuild`.
- Hosted Conda setup and test jobs succeed.
- PR `#10` is merged at `2ef28f27f9292b7a716f2e6d1c0d1153ef181bb9`.
- All 25 applicable PR-head hosted checks are recorded with job URLs.

## Authoritative Inputs

- Fork issue `#9`, fork PR `#10`, PR head
  `282864724255a910563901e84f5c7dec3bced433`, and merge commit
  `2ef28f27f9292b7a716f2e6d1c0d1153ef181bb9`.
- Workflow and recipe implementation at the merge commit.

## Evidence Boundary

The hosted checks ran in the controlled fork. They are first-party operational
evidence, not independent validation and not evidence of upstream acceptance.
The post-merge deployment workflow failed during fork publishing; publication is
outside this repair's acceptance contract and is recorded without being hidden.

## Out of Scope

- Any upstream workflow change.
- Publication credentials or a fork package release.
