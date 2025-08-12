from typing import List, Type

from pydantic import BaseModel
from wexample_filestate.operation.abstract_operation import AbstractOperation


class AbstractOperationsProvider(BaseModel):
    @staticmethod
    def get_operations() -> List[Type["AbstractOperation"]]:
        return []
