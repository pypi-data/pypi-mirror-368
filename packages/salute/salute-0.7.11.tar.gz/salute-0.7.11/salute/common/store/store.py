from abc import abstractmethod, ABC
from typing import Dict, Any, Optional


class StoreProvider(ABC):
    NAME = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    async def init(self, *args, **kwargs):
        pass

    @abstractmethod
    async def connect(self, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    async def save(self, key: str, value: Dict[str, Any], raw_table: str) -> bool:
        pass

    @abstractmethod
    async def save_or_update(
        self, key: str, value: Dict[str, Any], raw_table: str
    ) -> bool:
        pass

    @abstractmethod
    async def get(self, key: str, raw_table: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def remove(self, key: str, raw_table: str) -> bool:
        pass
