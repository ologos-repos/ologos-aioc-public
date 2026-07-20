from ologos_aioc import ExecutionContext


def test_new_generates_run_id():
    ctx = ExecutionContext.new()
    assert ctx.run_id
    assert ctx.actor_id is None


def test_new_carries_fields():
    ctx = ExecutionContext.new(actor_id="a", session_id="s", purpose="p", domain="d", metadata={"k": "v"})
    assert ctx.actor_id == "a"
    assert ctx.session_id == "s"
    assert ctx.purpose == "p"
    assert ctx.domain == "d"
    assert ctx.metadata == {"k": "v"}


def test_frozen():
    ctx = ExecutionContext.new()
    try:
        ctx.actor_id = "x"
        assert False, "should not be assignable"
    except Exception:
        pass
