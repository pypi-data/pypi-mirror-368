from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseCallContext(ABC):
    @abstractmethod
    def get_user_id(self) -> Optional[str]: ...

    @abstractmethod
    def get_turn_id(self) -> Optional[str]: ...

    @abstractmethod
    def get_meta(self, key: str) -> Optional[Any]: ...

    @abstractmethod
    def set_meta(self, key: str, value: Any) -> None: ...
