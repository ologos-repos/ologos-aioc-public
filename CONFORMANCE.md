# Conformance

These are the behavioral requirements this reference kernel actually
satisfies, each backed by a real test in `tests/test_conformance.py` — not
aspirational claims. This is the public, checkable contract; it says
nothing about what a governed deployment's policy *content* must be, only
what the *mechanism* guarantees.

| ID | Requirement |
|---|---|
| AIOC-CORE-001 | Every run shall possess a unique execution identifier, present on the result whether the run succeeds or fails. |
| AIOC-CORE-002 | Every tool-call request shall pass through a governance decision point before its handler is invoked. |
| AIOC-CORE-003 | A DENY or REQUIRE_CONFIRMATION decision shall prevent the tool's handler from being invoked at all — not merely be logged after the fact. |
| AIOC-CORE-004 | Every run that terminates, successfully or not, shall emit a terminal outcome event when an evidence recorder is supplied. |
| AIOC-CORE-005 | Model selection shall be a separate concern from orchestration logic — the orchestrator accepts an already-resolved model, it does not perform routing itself. |
| AIOC-CORE-006 | Tool schemas shall be exposed in a provider-consumable form before dispatch, derived from the same registration a handler is invoked from (no separate schema-authoring step). |
| AIOC-CORE-007 | Evidence capture shall be explicit, not implicit — a run with no recorder supplied produces no evidence records. |
| AIOC-CORE-008 | Side-effecting capabilities shall be distinguishable from observational ones via capability metadata. |

Run the conformance suite:

```bash
pytest tests/test_conformance.py -v
```

## What this does *not* certify

Conformance here means the mechanism works as described — a DENY decision
really does block execution, an evidence recorder really does capture every
stage. It does not certify:

- that any particular policy content is correct or complete;
- that the illustrative evidence recorders are tamper-evident, signed, or
  audit-grade (they explicitly are not — see `ologos_aioc/evidence.py`);
- fitness for any regulated, safety-critical, or production deployment.

See [`IP-BOUNDARY.md`](IP-BOUNDARY.md) for what a governed deployment adds
on top of this contract.
