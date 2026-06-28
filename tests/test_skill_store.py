from src.memory.skills import SkillStore


def test_success_rate_ranks_best_skill_first():
    store = SkillStore()
    store.extract("a", "do a")
    store.record_success("a")
    store.extract("b", "do b")
    store.record_failure("b")

    ranked = store.best(top_k=2)
    assert ranked[0].name == "a"
    assert ranked[0].success_rate == 1.0


def test_combine_creates_composite_skill():
    store = SkillStore()
    store.extract("login", "enter credentials")
    store.extract("checkout", "submit payment")

    composite = store.combine("login", "checkout", "purchase_flow")
    assert composite is not None
    assert composite.composed_of == ["login", "checkout"]
    assert "enter credentials" in composite.procedure
    assert "submit payment" in composite.procedure


def test_combine_returns_none_for_missing_skill():
    store = SkillStore()
    store.extract("login", "enter credentials")
    assert store.combine("login", "missing", "x") is None
