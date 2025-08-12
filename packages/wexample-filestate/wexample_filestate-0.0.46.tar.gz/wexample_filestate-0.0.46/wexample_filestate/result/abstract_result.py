from __future__ import annotations

from typing import List
from pydantic import BaseModel

from wexample_filestate.item.abstract_item_target import AbstractItemTarget
from wexample_filestate.operation.abstract_operation import AbstractOperation

class AbstractResult(BaseModel):
    state_manager: "AbstractItemTarget"
    operations: List[AbstractOperation] = []
    rollback: bool = False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __str__(self) -> str:
        return f"{self.__repr__}"
