## Summary

## Checklist

- [ ] `pytest` passes locally
- [ ] Checked against [`IP-BOUNDARY.md`](IP-BOUNDARY.md) — nothing here is derived from a client engagement or exposes production policy/identity/evidence internals
- [ ] If this adds a behavioral guarantee, it's backed by a new requirement in `CONFORMANCE.md` + a test in `tests/test_conformance.py`, not just a docstring claim
- [ ] New public API is exported from `ologos_aioc/__init__.py` if it's meant to be used directly
