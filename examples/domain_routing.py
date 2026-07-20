"""Demonstrates capability-aware routing: two synthetic models, routed by
tag, capability domain, and risk -- not just a name lookup.

    python3 examples/domain_routing.py
"""
from ologos_aioc import CapabilityDescriptor, EchoProvider, ModelCatalog


def main() -> None:
    catalog = ModelCatalog()

    catalog.register(
        "demo-fast",
        EchoProvider(canned_text="(fast) quick synthetic answer"),
        tags={"fast", "low-cost"},
        capability=CapabilityDescriptor(
            capability_id="demo-fast-completion", domain="demo-general",
            risk="low", side_effecting=False, tags=frozenset({"chat"}),
        ),
    )
    catalog.register(
        "demo-reasoning",
        EchoProvider(canned_text="(reasoning) slower, more deliberate synthetic answer"),
        tags={"reasoning"},
        capability=CapabilityDescriptor(
            capability_id="demo-reasoning-completion", domain="demo-analysis",
            risk="medium", side_effecting=False, tags=frozenset({"chat", "analysis"}),
        ),
    )

    for tag in ("fast", "reasoning"):
        entry = catalog.route(tag)
        cap = entry.capability
        print(f"route({tag!r}) -> {entry.name}  domain={cap.domain}  risk={cap.risk}")
        response = entry.provider.complete([{"role": "user", "content": "hello"}])
        print(f"  response: {response.text}")


if __name__ == "__main__":
    main()
