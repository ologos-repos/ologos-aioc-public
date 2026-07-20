from ologos_aioc import CapabilityDescriptor, EchoProvider, ModelCatalog, Tool, ToolRegistry


def test_model_entry_carries_capability():
    catalog = ModelCatalog()
    cap = CapabilityDescriptor(capability_id="demo-fast", domain="demo", risk="low", side_effecting=False)
    catalog.register("fast", EchoProvider(), tags={"fast"}, capability=cap)
    entry = catalog.get("fast")
    assert entry.capability is cap
    assert entry.capability.side_effecting is False


def test_tool_carries_capability():
    cap = CapabilityDescriptor(
        capability_id="demo-restart-service", domain="demo-infraops", risk="high",
        side_effecting=True, confirmation_recommended=True, tags=frozenset({"disruptive"}),
    )
    tool = Tool(name="restart_service", description="Restart a demo service",
                parameters={"type": "object", "properties": {}}, handler=lambda: "ok", capability=cap)
    registry = ToolRegistry()
    registry.register(tool)
    assert registry.get("restart_service").capability.risk == "high"
    assert registry.get("restart_service").capability.confirmation_recommended is True
