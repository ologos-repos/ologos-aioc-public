from ologos_aioc import DecisionDisposition, GovernanceDecision


def test_allow_helper_defaults():
    decision = GovernanceDecision.allow()
    assert decision.disposition is DecisionDisposition.ALLOW
    assert decision.reason_code == "DEMO_ALLOWED"


def test_decision_carries_obligations():
    decision = GovernanceDecision(DecisionDisposition.MODIFY, "DEMO_MODIFY", obligations=("redact:field_x",))
    assert decision.obligations == ("redact:field_x",)
