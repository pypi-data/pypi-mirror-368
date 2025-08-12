from __future__ import annotations

from typing import TYPE_CHECKING, cast

from wexample_config.config_value.config_value import ConfigValue
from wexample_filestate.config_option.content_filter_config_option import ContentFilterConfigOption
from wexample_filestate.operation.file_write_operation import FileWriteOperation
from wexample_helpers.helpers.file import file_read

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType
    from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class ApplyContentFilterOperation(FileWriteOperation):
    _original_path_str: str

    @staticmethod
    def applicable_option(
        target: "TargetFileOrDirectoryType",
        option: "AbstractConfigOption"
    ) -> bool:
        from wexample_filestate.config_option.content_filter_config_option import (
            ContentFilterConfigOption,
        )

        if isinstance(option, ContentFilterConfigOption):
            return target.source is not None

        return False

    def describe_before(self) -> str:
        return "TO_FILTER"

    def describe_after(self) -> str:
        return "FILTERED"

    def description(self) -> str:
        return "Apply given filters on content"

    def apply(self) -> None:
        filters = cast(ContentFilterConfigOption, self.target.get_option(ContentFilterConfigOption)).get_filters()

        self._target_file_write(
            content=ConfigValue.apply_filters(
                content=file_read(self._get_target_file_path(target=self.target)),
                filters=filters,
            )
        )
