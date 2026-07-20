from ologos_aioc.providers import EchoProvider


def test_echo_no_tools():
    provider = EchoProvider()
    response = provider.complete([{"role": "user", "content": "hello world"}])
    assert response.text == "(echo) hello world"
    assert response.tool_calls == []


def test_echo_canned_text():
    provider = EchoProvider(canned_text="fixed reply")
    response = provider.complete([{"role": "user", "content": "anything"}])
    assert response.text == "fixed reply"


def test_echo_emits_tool_call_when_named_in_prompt():
    provider = EchoProvider()
    tools = [{"type": "function", "function": {"name": "weather", "description": "d", "parameters": {}}}]
    response = provider.complete([{"role": "user", "content": "call weather"}], tools=tools)
    assert response.text is None
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "weather"


def test_echo_returns_final_answer_after_tool_result():
    provider = EchoProvider()
    messages = [
        {"role": "user", "content": "call weather"},
        {"role": "tool", "tool_call_id": "call_1", "content": "sunny"},
    ]
    response = provider.complete(messages)
    assert "sunny" in response.text
    assert response.tool_calls == []
