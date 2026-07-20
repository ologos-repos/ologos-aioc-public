from pathlib import Path

from ologos_aioc import load_profile

PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"


def test_load_infraops_profile():
    profile = load_profile(PROFILES_DIR / "demo-infraops.yaml")
    assert profile.id == "demo-infraops"
    assert profile.level == "domain"
    assert len(profile.capabilities) == 2
    restart = next(c for c in profile.capabilities if c.id == "demo-restart-service")
    assert restart.side_effecting is True
    assert restart.confirmation_recommended is True
    assert "operations" in profile.views


def test_load_cyberops_profile():
    profile = load_profile(PROFILES_DIR / "demo-cyberops.yaml")
    assert profile.id == "demo-cyberops"
    assert len(profile.capabilities) == 2
    assert "diagnostics" in profile.views


def test_two_profiles_have_distinct_capability_surfaces():
    infraops = load_profile(PROFILES_DIR / "demo-infraops.yaml")
    cyberops = load_profile(PROFILES_DIR / "demo-cyberops.yaml")
    infraops_ids = {c.id for c in infraops.capabilities}
    cyberops_ids = {c.id for c in cyberops.capabilities}
    assert infraops_ids.isdisjoint(cyberops_ids)
