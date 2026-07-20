# Architecture

## The operating model

An AI Operations Center (AIOC) is the enterprise operating capability
responsible for governing, orchestrating, observing, assuring, and
evidencing AI-enabled work across models, agents, tools, data, services,
and human operators. That's a broader claim than "an agent library," and
it's worth being explicit about the shape of the whole thing before
describing what's in this particular repository.

```
Identity and purpose
        |
Authority and governance
        |
Model and capability routing
        |
Governed execution
        |
Observation and evidence
        |
Domain operating experience
```

Six layers, each a distinct architectural concern:

1. **Identity and purpose** — who is acting, on whose behalf, for what
   reason. Represented here by `ExecutionContext`; the actual identity
   system that populates it (authentication, tenancy, role resolution) is
   not part of this open core.
2. **Authority and governance** — what that actor is permitted to do.
   Represented here by `GovernanceHook` and `GovernanceDecision`; the
   actual policy — precedence, entitlement, real reason codes — is not
   part of this open core. Ologos's own governance layer draws on
   published research into multi-mode AI operation (see *Related work* in
   the README) — the open core exposes the seam that research informs,
   not its operational implementation.
3. **Model and capability routing** — which resource (model or tool)
   handles a given piece of work, and what that resource's risk profile
   is. Represented here by `ModelCatalog` and `CapabilityDescriptor`; a
   real deployment's routing policy (cost, latency, availability,
   compliance) is not part of this open core.
4. **Governed execution** — the actual dispatch-and-tool-call loop, with
   governance decisions enforced *before* a handler runs, not logged after
   the fact. This is what `Orchestrator` does, and it's fully implemented
   here — the loop, the gate, and the proof that the gate works
   (`CONFORMANCE.md`).
5. **Observation and evidence** — proof that governed work happened.
   Represented here by `OperationStage`, `EvidenceEvent`, and two
   illustrative recorders; a production evidence plane (chaining, signing,
   retention) is not part of this open core.
6. **Domain operating experience** — how the same control plane presents
   differently to different operating domains. Represented here by the
   domain-profile contract (`ologos_aioc/profiles.py`, `profiles/*.yaml`);
   real console implementations and enterprise domain inventories are not
   part of this open core.

## What's fully implemented vs. what's a contract

| Layer | This repo | A governed deployment |
|---|---|---|
| Identity and purpose | `ExecutionContext` (generic carrier) | Real authentication, tenancy, role resolution |
| Authority and governance | `GovernanceHook`, decision gate (enforced) | Real policy content and precedence |
| Model and capability routing | `ModelCatalog`, tag-based routing | Cost/latency/compliance-aware routing |
| Governed execution | `Orchestrator` — fully implemented | (same code, governed policy plugged in) |
| Observation and evidence | Illustrative recorders | Tamper-evident, signed, retained evidence |
| Domain operating experience | Declarative profile contract | Real consoles, navigation, administration |

The middle layer — governed execution — is the one layer where "this repo"
and "a governed deployment" are the *same code*, not a stand-in. That's
deliberate: the orchestration loop is not the differentiator, so there's
no reason to hold it back. See [`IP-BOUNDARY.md`](IP-BOUNDARY.md) for the
explicit publish/reserve line, and [`CONFORMANCE.md`](CONFORMANCE.md) for
what's checkable, not just described.

## Module map

| Module | Contents |
|---|---|
| `context.py` | `ExecutionContext` |
| `events.py` | `OperationStage`, `EvidenceEvent` |
| `decisions.py` | `DecisionDisposition`, `GovernanceDecision` |
| `evidence.py` | `EvidenceRecorder` + illustrative implementations |
| `capabilities.py` | `CapabilityDescriptor` |
| `governance.py` | `GovernanceHook`, the decision gate, block exceptions |
| `providers.py` | `ModelProvider` + implementations |
| `catalog.py` | `ModelCatalog`, `ModelEntry` |
| `tools.py` | `Tool`, `ToolRegistry` |
| `profiles.py` | Domain-console profile loader |
| `orchestrator.py` | The loop that ties all of the above together |
