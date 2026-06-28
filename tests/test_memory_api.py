from src.memory.api import Memory


def test_store_and_retrieve_episodic():
    memory = Memory()
    memory.store("user likes coffee")
    result = memory.retrieve("coffee")
    assert any("coffee" in e.content for e in result["episodic"])


def test_consolidate_promotes_recurring_episodes():
    memory = Memory()
    memory.store("user likes coffee")
    memory.store("user likes coffee")
    promoted = memory.consolidate()
    assert promoted == 1
    assert memory.semantic.has_fact("user likes coffee")


def test_skill_extract_from_episode_with_plan():
    memory = Memory()
    memory.store("greet user", context={"plan": "say hello"})
    skill = memory.skill_extract(0)
    assert skill is not None
    assert skill.procedure == "say hello"


def test_skill_extract_returns_none_without_plan():
    memory = Memory()
    memory.store("no plan event")
    assert memory.skill_extract(0) is None
