from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Type, TYPE_CHECKING

from pydantic import BaseModel

from wexample_helpers.helpers.array import array_swap
from wexample_prompt.responses.base_prompt_response import BasePromptResponse

if TYPE_CHECKING:
    from wexample_filestate.const.state_items import TargetFileOrDirectory
    from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class AbstractOperation(BaseModel, ABC):
    applied: bool = False
    target: "TargetFileOrDirectory"
    _tty_width: int = 80

    @classmethod
    def applicable(cls, target: "TargetFileOrDirectory") -> bool:
        for option in target.options.values():
            if cls.applicable_option(
                target=target,
                option=option) is True:
                return True

        return False

    @staticmethod
    @abstractmethod
    def applicable_option(target: "TargetFileOrDirectory", option: "AbstractConfigOption") -> bool:
        pass

    @abstractmethod
    def apply(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def describe_before(self) -> str:
        pass

    @abstractmethod
    def describe_after(self) -> str:
        pass

    def dependencies(self) -> List[Type["AbstractOperation"]]:
        return []

    def to_prompt_response(self, rollback: bool) -> BasePromptResponse:
        lines = [
            f'{"TASK" if not rollback else "ROLLBACK"} '.ljust(self._tty_width, "_")
        ]

        before, after = array_swap(
            [
                self.describe_before(),
                self.describe_after(),
            ],
            do_swap=rollback,
        )

        lines.extend(
            [
                f"{self.target.get_item_title()}: {self.target.get_resolved()}",
                f"{self.description()}:",
                f"    Before: {before}",
                f"    After: {after}",
            ]
        )

        return BasePromptResponse.create_from_text_lines(lines)
