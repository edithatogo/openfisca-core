# OpenFisca YAML portability and loss boundaries

This guide defines the supported boundary for deterministic adapters that turn
external fixtures or process cases into OpenFisca YAML tests. It applies to
OpenFisca Core 44.x and the YAML test runner implemented by
`openfisca_core.tools.test_runner` and `SimulationBuilder.build_from_dict`.
Country packages remain authoritative for their entities, roles, variables,
enums, formulas, input frequencies, and valid periods.

OpenFisca Core does not provide a universal source-format converter. An adapter
MUST declare its source format and version, target country package and version,
OpenFisca Core version, assumptions, and diagnostics. It MUST be deterministic:
runtime AI decisions and silent coercion are outside this contract.

## Mapping classification

| Source meaning | Classification | OpenFisca YAML representation |
| --- | --- | --- |
| Stable source record identifier | Lossless | Entity instance key, preserved verbatim as a YAML string. |
| Person and group membership | Lossless when explicit | Person entities plus country-package group entities and role lists. |
| Role with an exact country-package match | Lossless | The declared role key containing referenced person identifiers. |
| Variable with an exact semantic and unit match | Lossless | Country-package variable name under the owning entity. |
| Explicit period with matching frequency | Lossless | ISO year, month, day, or other period syntax accepted by the target variable. |
| Enum with an exact declared member match | Lossless | Declared enum member name as a string. |
| Explicit zero or `false` | Lossless | Preserve the scalar; never treat it as missing. |
| Expected output with exact variable and period semantics | Lossless | `output` variable, entity, or entity-instance form supported by the YAML runner. |
| Source role that deterministically aggregates to one target role | Lossy | Map only under a named adapter assumption and emit `OFC-W-ROLE-AGGREGATED`. |
| Source period requiring deterministic frequency conversion | Lossy | Convert only with a documented allocation rule and emit `OFC-W-PERIOD-COERCED`. |
| Decimal money | Lossy at the runtime boundary | Parse from a decimal string, apply an explicit currency/minor-unit and rounding rule, then emit an OpenFisca numeric scalar and `OFC-W-DECIMAL-QUANTIZED`. Python floats and YAML numeric scalars do not preserve arbitrary decimal lexical precision. |
| Omitted value | Conditional | Omit the variable. Never emit its default. Use `Simulation.is_input` or `get_input_state` where provenance must distinguish omission from explicit input. |
| Unknown entity, role, variable, enum member, unit, or period meaning | Unsupported | Do not emit runnable YAML; return an error diagnostic. |
| Multiple possible memberships or roles without a deterministic rule | Unsupported | Fail with `OFC-E-AMBIGUOUS-MAPPING`. |
| Source logic, workflow state, evidence, confidence, or legal provenance | Unsupported | Keep in a sidecar or source system; OpenFisca YAML tests do not represent these semantics. |
| Expected interval, probability, relational assertion, or unordered collection | Unsupported | Fail unless the adapter has a separately versioned, deterministic assertion extension. |

## Canonical shape

```yaml
- name: explicit inputs and entity membership
  period: 2017-01
  input:
    persons:
      person-1:
        salary: 0
      person-2: {}
    households:
      household-1:
        adults: [person-1, person-2]
  output:
    persons:
      person-1:
        income_tax: 0
```

`salary: 0` is explicit input. The absent `salary` for `person-2` is missing
source input and MUST remain absent. A top-level `period` is only a shortcut for
values whose target variables accept that period; use per-variable period maps
when inputs or outputs span periods.

Entity and role names are not portable across country packages. Adapters MUST
resolve them against the loaded target system. Person identifiers referenced by
roles MUST exist, each membership constraint imposed by the target entity model
MUST hold, and adapter output order MUST be stable.

Enum values MUST use target enum member names, not labels or ordinal positions.
Expected outputs MUST express values calculable by the pinned target package;
formula equivalence across package versions is not implied by YAML equivalence.

## Diagnostics and fail-closed behavior

Every conversion MUST produce a diagnostics document conforming to
[`yaml-conversion-diagnostics.schema.json`](./yaml-conversion-diagnostics.schema.json).
The outcome is `success` only for lossless conversion, `success_with_warnings`
when every loss is covered by a named deterministic assumption, and `failure`
when any error exists. On `failure`, `output_emitted` MUST be `false` and no
runnable YAML may be published.

Required error codes are:

- `OFC-E-UNKNOWN-ENTITY`, `OFC-E-UNKNOWN-ROLE`, and `OFC-E-UNKNOWN-VARIABLE`
- `OFC-E-UNKNOWN-ENUM`
- `OFC-E-PERIOD-UNSUPPORTED` and `OFC-E-UNIT-UNSUPPORTED`
- `OFC-E-AMBIGUOUS-MAPPING`
- `OFC-E-UNSUPPORTED-SEMANTIC`

Diagnostics use JSON Pointer in `source_path` and, when an output node exists,
`target_path`. Messages are explanatory only; automation MUST branch on
`severity` and `code`. Examples are maintained in
[`yaml-portability-examples`](./yaml-portability-examples/).

## Semantic-equivalence validation

An adapter release is acceptable only when it:

1. validates diagnostics against the bundled schema and checks outcome/error
   consistency;
2. parses generated YAML with `yaml.safe_load` and builds it with the pinned
   country package and OpenFisca Core runtime;
3. proves missing versus explicit zero/false with input-state queries;
4. verifies entity identifiers, memberships, roles, enum members, periods, and
   values against source fixtures;
5. executes expected outputs through `openfisca test`;
6. converts the same source twice and byte-compares canonical output and
   diagnostics; and
7. where reverse conversion exists, compares normalized source semantics, not
   YAML spelling, comments, anchors, key style, or key order.

YAML comments, anchors, aliases, quoting, formatting, and original numeric
lexemes are presentation details and are not round-trip guarantees. Runtime or
country-package upgrades require rerunning the equivalence suite; compatibility
is not assumed across OpenFisca Core major versions or country-package releases.

