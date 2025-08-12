from typing import Any, Optional
from collections import OrderedDict
from kradle.memory.abstract_memory import AbstractMemoryStore, Memory
import threading


class StandardMemory(AbstractMemoryStore):
    def __init__(
        self, max_size: int = 1000, participant_id: Optional[str] = None, run_id: Optional[str] = None
    ) -> None:
        self._memory: OrderedDict[str, Any] = OrderedDict()
        self._lock = threading.RLock()
        self._max_size = max_size
        self._participant_id = participant_id
        self._run_id = run_id

    def _get_key(self, key: str, participant_id: Optional[str] = None, run_id: Optional[str] = None) -> str:
        pid = participant_id or self._participant_id
        rid = run_id or self._run_id

        if rid and pid:
            return f"{rid}:{pid}:{key}"
        elif pid:
            return f"{pid}:{key}"
        else:
            return key

    def save_memory(
        self, key: str, data: Any, participant_id: Optional[str] = None, run_id: Optional[str] = None
    ) -> None:
        full_key = self._get_key(key, participant_id, run_id)
        with self._lock:
            if full_key in self._memory:
                del self._memory[full_key]
            elif len(self._memory) >= self._max_size:
                self._memory.popitem(last=False)
            self._memory[full_key] = data

    def load_memory(
        self, key: str, participant_id: Optional[str] = None, run_id: Optional[str] = None
    ) -> Optional[Any]:
        full_key = self._get_key(key, participant_id, run_id)
        with self._lock:
            if full_key not in self._memory:
                return None
            value = self._memory.pop(full_key)
            self._memory[full_key] = value
            return value

    def load_all_memory(self, participant_id: Optional[str] = None, run_id: Optional[str] = None) -> Memory:
        memory = Memory()
        pid = participant_id or self._participant_id
        rid = run_id or self._run_id

        if rid and pid:
            prefix = f"{rid}:{pid}:"
        elif pid:
            prefix = f"{pid}:"
        else:
            prefix = ""

        with self._lock:
            for key, value in self._memory.items():
                if key.startswith(prefix):
                    base_key = key[len(prefix) :] if prefix else key
                    memory.data[base_key] = value
        return memory

    def flush_all_memory(self, participant_id: Optional[str] = None, run_id: Optional[str] = None) -> None:
        pid = participant_id or self._participant_id
        rid = run_id or self._run_id

        if rid and pid:
            prefix = f"{rid}:{pid}:"
        elif pid:
            prefix = f"{pid}:"
        else:
            prefix = ""
        with self._lock:
            keys_to_remove = [k for k in self._memory.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                del self._memory[key]

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return self.load_memory(name, run_id=self._run_id)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self.save_memory(name, value, run_id=self._run_id)
