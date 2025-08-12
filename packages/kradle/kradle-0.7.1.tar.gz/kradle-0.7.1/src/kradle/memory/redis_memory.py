from typing import Any, Optional, cast
import redis
import json
from kradle.memory.abstract_memory import AbstractMemoryStore, Memory


class RedisMemory(AbstractMemoryStore):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        participant_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ):
        self._redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
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
        serialized = json.dumps(data)
        self._redis.set(full_key, serialized)

    def load_memory(
        self, key: str, participant_id: Optional[str] = None, run_id: Optional[str] = None
    ) -> Optional[Any]:
        full_key = self._get_key(key, participant_id, run_id)
        data = cast(Optional[str], self._redis.get(full_key))
        return json.loads(data) if data else None

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

        pattern = f"{prefix}*" if prefix else "*"

        for key in self._redis.scan_iter(pattern):
            base_key = key[len(prefix) :] if prefix else key
            memory.data[base_key] = self.load_memory(base_key, participant_id, run_id)
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
        pattern = f"{prefix}*" if prefix else "*"

        for key in self._redis.scan_iter(pattern):
            self._redis.delete(key)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return self.load_memory(name, run_id=self._run_id)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self.save_memory(name, value, run_id=self._run_id)
