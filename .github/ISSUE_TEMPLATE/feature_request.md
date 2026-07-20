---
name: Feature or scope question
about: Propose an addition, or ask whether something belongs in this repo
labels: enhancement
---

**What you want to add or change**

**Which side of the line is this on?** Check [`IP-BOUNDARY.md`](../../IP-BOUNDARY.md) first — architectural interfaces, generic lifecycle contracts, synthetic demonstrations, and reference tests are in scope; real policy content, identity/authority models, and production evidence mechanisms are not. If you're not sure, say so here and we'll figure it out before any code gets written.

**Does this need a new `CONFORMANCE.md` requirement?** If it's a behavioral guarantee (not just an API convenience), it should land as a numbered requirement backed by a test in `tests/test_conformance.py`, not just a docstring claim.
