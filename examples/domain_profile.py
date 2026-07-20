"""Demonstrates domain-console profiles: the same control plane, two
different declarative capability surfaces.

    python3 examples/domain_profile.py

Requires the 'profiles' extra: pip install 'ologos-aioc[profiles]'
"""
from pathlib import Path

from ologos_aioc import load_profile

PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"


def main() -> None:
    for filename in ("demo-infraops.yaml", "demo-cyberops.yaml"):
        profile = load_profile(PROFILES_DIR / filename)
        print(f"{profile.title}  ({profile.id})")
        print(f"  views: {', '.join(profile.views)}")
        for cap in profile.capabilities:
            flags = []
            if cap.side_effecting:
                flags.append("side-effecting")
            if cap.confirmation_recommended:
                flags.append("confirmation-recommended")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"  - {cap.id} (risk={cap.risk}){flag_str}")
        print()


if __name__ == "__main__":
    main()
