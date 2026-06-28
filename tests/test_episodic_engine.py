from src.memory.episodic import EpisodicMemory


def test_episode_captures_metadata():
    store = EpisodicMemory(db_path=":memory:")
    episode = store.store("deployed service", who="alice", where="prod", why="release 1.2")
    assert episode.who == "alice"
    assert episode.where == "prod"
    assert episode.why == "release 1.2"

    [reloaded] = store.all()
    assert reloaded.who == "alice"
    assert reloaded.where == "prod"
    assert reloaded.why == "release 1.2"


def test_hybrid_retrieval_finds_vector_similar_without_exact_substring():
    store = EpisodicMemory(db_path=":memory:")
    store.store("the cat sat on the mat")
    store.store("a cat sleeping on a mat")
    store.store("completely unrelated weather report")

    results = store.retrieve("cat mat", top_k=5)
    contents = [e.content for e in results]
    assert "the cat sat on the mat" in contents
    assert "a cat sleeping on a mat" in contents


def test_forget_before_evicts_old_episodes():
    import time

    store = EpisodicMemory(db_path=":memory:")
    store.store("old event")
    cutoff = time.time() + 0.01
    time.sleep(0.02)
    store.store("new event")

    evicted = store.forget_before(cutoff)
    assert evicted == 1
    remaining = [e.content for e in store.all()]
    assert "new event" in remaining
    assert "old event" not in remaining
