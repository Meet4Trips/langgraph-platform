import pytest

from agent.archive import example_graph

pytestmark = pytest.mark.anyio


@pytest.mark.langsmith
async def test_agent_simple_passthrough() -> None:
    inputs = {"changeme": "some_val"}
    res = await example_graph.ainvoke(inputs)
    assert res is not None
