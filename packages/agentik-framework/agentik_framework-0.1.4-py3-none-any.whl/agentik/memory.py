# agentik/memory.py
import abc
import json
from pathlib import Path
from typing import List


class MemoryBase(abc.ABC):
    @abc.abstractmethod
    def remember(self, context: str) -> None: ...
    @abc.abstractmethod
    def recall(self, query: str = "") -> List[str]: ...
    @abc.abstractmethod
    def summarize(self) -> str: ...


class DictMemory(MemoryBase):
    def __init__(self):
        self._data: List[str] = []
    def remember(self, context: str) -> None:
        self._data.append(context)
    def recall(self, query: str = "") -> List[str]:
        return [c for c in self._data if query.lower() in c.lower()] if query else list(self._data)
    def summarize(self) -> str:
        return "\n".join(self._data)


class JSONMemoryStore(MemoryBase):
    def __init__(self, filepath: str = "memory.json"):
        self.path = Path(filepath)
        if not self.path.exists():
            self._save([])
    def _load(self) -> List[str]:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []
    def _save(self, data: List[str]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    def remember(self, context: str) -> None:
        data = self._load()
        data.append(context)
        self._save(data)
    def recall(self, query: str = "") -> List[str]:
        data = self._load()
        return [c for c in data if query.lower() in c.lower()] if query else data
    def summarize(self) -> str:
        return "\n".join(self._load())
