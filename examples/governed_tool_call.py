"""Demonstrates the governance gate actually blocking a tool call.

    python3 examples/governed_tool_call.py

A synthetic "restart a demo service" tool is denied by a demo policy
before its handler ever runs — proving the mechanism, not just describing
it. Compare with basic_usage.py, where the same shape of call is allowed.
"""
from ologos_aioc import (
    ActionDenied,
    DecisionDisposition,
    EchoProvider,
    GovernanceDecision,
    ModelCatalog,
    NoOpGovernanceHook,
    Orchestrator,
    Tool,
    ToolRegistry,
)


class DenyDisruptiveActions(NoOpGovernanceHook):
    """A toy policy: deny any tool call whose name contains 'restart'.
    A governed deployment's real policy engine is not part of this open
    core -- this exists only to demonstrate that the gate is enforced."""

    def evaluate_tool_call(self, context, tool_name, arguments):
        if "restart" in tool_name:
            return GovernanceDecision(
                DecisionDisposition.DENY,
                reason_code="DEMO_DISRUPTIVE_ACTION_BLOCKED",
                message=f"{tool_name!r} is disruptive; denied by demo policy",
            )
        return GovernanceDecision.allow()


def restart_demo_service(service: str = "demo-web") -> str:
    return f"restarted {service}"  # should never actually run in this demo


def main() -> None:
    catalog = ModelCatalog()
    catalog.register("demo-model", EchoProvider(), tags={"fast"})

    tools = ToolRegistry()
    tools.register(Tool(
        name="restart_demo_service",
        description="Restart a demo service (synthetic, always denied by this demo's policy)",
        parameters={"type": "object", "properties": {"service": {"type": "string"}}},
        handler=restart_demo_service,
    ))

    orchestrator = Orchestrator(
        model=catalog.route("fast"),
        tools=tools,
        governance=DenyDisruptiveActions(),
    )

    try:
        orchestrator.run("please call restart_demo_service")
        print("UNEXPECTED: the call was allowed")
    except ActionDenied as exc:
        print(f"Blocked as expected: {exc}")
        print("The handler was never invoked -- restart_demo_service() did not run.")


if __name__ == "__main__":
    main()
