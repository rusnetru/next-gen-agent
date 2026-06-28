from src.agent.loop import Agent


def test_agent_step_returns_result():
    agent = Agent(db_path=":memory:")
    result = agent.step("hello")
    assert "hello" in result


def test_agent_stores_episode():
    agent = Agent(db_path=":memory:")
    agent.step("hello")
    retrieved = agent.memory.retrieve("hello")["episodic"]
    assert len(retrieved) == 1
