from src.evolution.skill_evolution import SkillEvolutionEngine
from src.memory.api import Memory


def test_extract_from_successful_episodes_skips_failures():
    memory = Memory(db_path=":memory:", consolidate_every=0)
    memory.store("deploy service", context={"plan": "run deploy.sh", "success": True})
    memory.store("flaky step", context={"plan": "retry", "success": False})

    engine = SkillEvolutionEngine(memory)
    extracted = engine.extract_from_successful_episodes()

    assert [s.name for s in extracted] == ["deploy service"]
    assert memory.skills.all()["deploy service"].successes == 1


def test_rank_orders_by_success_rate():
    memory = Memory(db_path=":memory:", consolidate_every=0)
    memory.skills.extract("a", "do a")
    memory.skills.record_success("a")
    memory.skills.extract("b", "do b")
    memory.skills.record_failure("b")

    engine = SkillEvolutionEngine(memory)
    ranked = engine.rank(top_k=2)
    assert ranked[0].name == "a"


def test_auto_combine_sequential_pairs_creates_composite():
    memory = Memory(db_path=":memory:", consolidate_every=0)
    for _ in range(2):
        memory.store("login", context={"plan": "enter credentials", "success": True})
        memory.store("checkout", context={"plan": "submit payment", "success": True})
        memory.skill_extract(memory.episodic.count() - 2)
        memory.skill_extract(memory.episodic.count() - 1)

    engine = SkillEvolutionEngine(memory)
    combined = engine.auto_combine_sequential_pairs(min_co_occurrences=2)

    assert any(s.name == "login+checkout" for s in combined)
    assert memory.skills.all()["login+checkout"].composed_of == ["login", "checkout"]
