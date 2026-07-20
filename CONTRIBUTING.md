# Contributing

Issues and PRs welcome.

```bash
git clone https://github.com/ologos-repos/ologos-aioc-public.git
cd ologos-aioc-public
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Keep additions within [`IP-BOUNDARY.md`](IP-BOUNDARY.md): architectural
interfaces, generic lifecycle contracts, synthetic demonstrations, and
reference tests are in scope. Real policy content, identity/authority
models, production evidence mechanisms, and anything derived from a
specific deployment or client engagement are not — see that document
before opening a PR that touches `governance.py`, `evidence.py`, or
`profiles/`. If you're unsure which side of the line something falls on,
open an issue first.

New behavioral guarantees should land as a numbered requirement in
[`CONFORMANCE.md`](CONFORMANCE.md) backed by a real test in
`tests/test_conformance.py`, not just a docstring claim.
