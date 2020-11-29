from typing import Any, List, Optional

from .targets import BaseTarget


class BaseFilter:
    support_list_condition: bool = True
    list_condition_key: Optional[str] = None

    def __init__(self) -> None:
        pass

    @property
    def list_condition_value(self) -> Any:
        raise NotImplementedError

    def filter(self, targets: List[BaseTarget]) -> List[BaseTarget]:
        raise NotImplementedError
