from typing import Any, Optional
from abc import ABC, abstractmethod


class Memory:
    def __init__(self) -> None:
        self.data: dict[str, Any] = {}

    def __getitem__(self, key: str) -> Any:
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def __getattr__(self, name: str) -> Any:
        return self.data.get(name)

    def __str__(self) -> str:
        return str(self.data)


class AbstractMemoryStore(ABC):
    @abstractmethod
    def save_memory(
        self, key: str, data: Any, participant_id: Optional[str] = None, run_id: Optional[str] = None
    ) -> None:
        pass

    @abstractmethod
    def load_memory(
        self, key: str, participant_id: Optional[str] = None, run_id: Optional[str] = None
    ) -> Optional[Any]:
        pass

    @abstractmethod
    def load_all_memory(self, participant_id: Optional[str] = None, run_id: Optional[str] = None) -> Memory:
        pass

    @abstractmethod
    def flush_all_memory(self, participant_id: Optional[str] = None, run_id: Optional[str] = None) -> None:
        pass
