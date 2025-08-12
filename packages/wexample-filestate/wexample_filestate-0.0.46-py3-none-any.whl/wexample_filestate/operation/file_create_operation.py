from __future__ import annotations

import os
from typing import TYPE_CHECKING, Union, cast

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.config_option.default_content_config_option import (
    DefaultContentConfigOption,
)
from wexample_filestate.enum.scopes import Scope
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)

if TYPE_CHECKING:
    from wexample_filestate.item.item_target_directory import (
        ItemTargetDirectory,
    )
    from wexample_filestate.item.item_target_file import (
        ItemTargetFile,
    )


class FileCreateOperation(FileManipulationOperationMixin, AbstractOperation):
    _original_path_str: str

    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.LOCATION

    @staticmethod
    def applicable_option(
            target: Union["ItemTargetDirectory", "ItemTargetFile"],
            option: "AbstractConfigOption"
    ) -> bool:
        return (
                target.source is None
                and FileManipulationOperationMixin.option_should_exist_is_true(target)
        )

    def describe_before(self) -> str:
        return "MISSING"

    def describe_after(self) -> str:
        return "CREATED"

    def description(self) -> str:
        return "Create missing file"

    def apply(self) -> None:
        self._original_path_str = self.target.get_resolved()

        if self.target.is_file():
            local_file = self.target.get_local_file()

            default_content = cast(
                DefaultContentConfigOption,
                self.target.get_option(DefaultContentConfigOption),
            )

            if default_content:
                default_content_option = self.target.get_option_value(DefaultContentConfigOption)

                if default_content_option:
                    local_file.write(default_content_option.get_str())
                else:
                    local_file.touch()
            else:
                local_file.touch()

        elif self.target.is_directory():
            os.mkdir(self._original_path_str)

    def undo(self) -> None:
        if self.target.is_file():
            os.remove(self._original_path_str)
        elif self.target.is_directory():
            # Do not remove recursively, as for now it only can be created empty with mkdir.
            os.rmdir(self._original_path_str)
