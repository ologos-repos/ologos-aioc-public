# Contributing

Issues and PRs welcome.

```bash
git clone https://github.com/ologos-repos/ologos-aioc-public.git
cd ologos-aioc-public
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Keep additions to the core scope: model-agnostic dispatch, tool-calling,
and the governance seam. Governed/enterprise features (identity, multi-tenant
policy, audit persistence, deployment patterns) are intentionally out of
scope for this repo — see the README's "Why this exists" section.
