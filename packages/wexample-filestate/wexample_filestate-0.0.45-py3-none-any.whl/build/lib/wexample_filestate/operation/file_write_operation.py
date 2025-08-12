from __future__ import annotations

import os
from typing import TYPE_CHECKING
from wexample_filestate.config_option.content_config_option import ContentConfigOption
from wexample_filestate.config_option.should_contain_lines_config_option import ShouldContainLinesConfigOption
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)
from wexample_helpers.helpers.file import file_read, file_write

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType
    from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class FileWriteOperation(FileManipulationOperationMixin, AbstractOperation):
    @staticmethod
    def applicable_option(target: "TargetFileOrDirectoryType", option: "AbstractConfigOption") -> bool:
        if isinstance(option, ContentConfigOption):
            current_content = file_read(target.get_resolved()) if os.path.exists(target.get_resolved()) else ""
            new_content = target.get_option_value(ContentConfigOption).get_str()
            return current_content != new_content

        if isinstance(option, ShouldContainLinesConfigOption):
            required_lines = target.get_option_value(ShouldContainLinesConfigOption)
            if not os.path.exists(target.get_resolved()):
                return True
            current_content = file_read(target.get_resolved())
            current_lines = current_content.splitlines()
            return any(line not in current_lines for line in required_lines)

        return False

    def describe_before(self) -> str:
        return "CURRENT_CONTENT"

    def describe_after(self) -> str:
        return "REWRITTEN_CONTENT"

    def description(self) -> str:
        return "Regenerate file content"

    def _target_file_write(self, content: str):
        self._backup_target_file()
        file_path = self._get_target_file_path(target=self.target)
        file_write(file_path, content=content)

    def apply(self) -> None:
        content_option = self.target.get_option(ContentConfigOption)
        should_contain_lines_option = self.target.get_option(ShouldContainLinesConfigOption)
        updated_content = None

        if content_option is not None:
            updated_content = self.target.get_option_value(ContentConfigOption).get_str()

        if should_contain_lines_option is not None:
            from wexample_helpers.helpers.string import string_append_missing_lines

            # Initialize content from existing file or empty string if file doesn't exist
            if updated_content is None:
                updated_content = file_read(self.target.get_resolved()) if os.path.exists(
                    self.target.get_resolved()) else ""

            updated_content = string_append_missing_lines(
                lines=self.target.get_option_value(ShouldContainLinesConfigOption).get_list(),
                content=updated_content
            )

        if updated_content is not None:
            self._target_file_write(
                content=updated_content
            )

    def undo(self) -> None:
        self._restore_target_file()
