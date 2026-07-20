# IP boundary — what's published vs. what's reserved

Ologos treats disclosure as a deliberate decision, not an accident of what
happened to get open-sourced first. This document states that decision
plainly, so the boundary is legible rather than implicit.

## Published here

- Architectural interfaces: `ExecutionContext`, `OperationStage`,
  `GovernanceDecision`, `EvidenceEvent`, `CapabilityDescriptor`, and the
  domain-profile contract.
- The generic operational lifecycle (request → model dispatch → tool
  execution → response release → completion) as a named sequence.
- A synthetic, in-process governance gate demonstrating that a decision
  can block a tool handler from running.
- Non-production evidence recorders (in-memory, JSON-lines) that show the
  *shape* of an evidence plane, not a real one.
- Reference tests proving the mechanism (see [`CONFORMANCE.md`](CONFORMANCE.md)).
- Fictional, illustrative domain-console profiles.

## Reserved — Ologos's governed enterprise product (ologos.co/aioc)

- Real identity and authority models: who an actor is, what they're
  entitled to, how that's established and revoked.
- Policy content: actual precedence rules, conflict resolution, the real
  reason-code catalog, and the conditions under which each disposition
  applies to a real action.
- Grant, delegation, and override mechanisms.
- Production evidence mechanisms: chaining, signing, tamper-evidence,
  redaction, retention, and export controls.
- Production model-risk scoring and prompt-policy enforcement.
- Real domain and console inventories, navigation, and administration.
- Deployment topology, including sovereign/disconnected operation
  patterns.
- Service/tool catalogs, credential boundaries, and connector
  implementations for any specific integration.
- Anything derived from a specific client engagement — requirements,
  architecture decisions, evidence records, or delivery artifacts. Nothing
  in this repository is extracted from client work; it is independently
  written to demonstrate the same architectural pattern in the abstract.

## The rule

**Publish the architectural grammar, lifecycle contracts, conformance
expectations, and synthetic demonstrations. Retain the operating logic,
policy content, enterprise schemas, deployment internals, and production
integrations.**

If you're contributing and unsure which side of this line something falls
on, open an issue before a PR — this boundary is enforced by review, not
tooling, and getting it wrong is cheap to fix before merge and expensive
after.
