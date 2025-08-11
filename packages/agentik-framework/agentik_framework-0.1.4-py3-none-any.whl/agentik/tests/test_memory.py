"""
Tests for memory backends: Dict and JSON memory.
"""

from agentik.memory import DictMemory, JSONMemoryStore

def test_dict_memory():
    mem = DictMemory()
    mem.remember("test")
    assert "test" in mem.recall()

def test_json_memory(tmp_path):
    mem_file = tmp_path / "memory.json"
    mem = JSONMemoryStore(filepath=str(mem_file))
    mem.remember("persisted")
    assert "persisted" in mem.recall()
    assert "persisted" in mem.summarize()
