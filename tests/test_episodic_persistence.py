from src.memory.episodic import EpisodicMemory


def test_episodes_persist_across_connections(tmp_path):
    db_path = tmp_path / "memory.db"

    store1 = EpisodicMemory(db_path=db_path)
    store1.store("first session event")
    store1.close()

    store2 = EpisodicMemory(db_path=db_path)
    episodes = store2.all()
    store2.close()

    assert len(episodes) == 1
    assert episodes[0].content == "first session event"
