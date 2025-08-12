from __future__ import annotations

from typing import TYPE_CHECKING, cast

from wexample_config.config_value.config_value import ConfigValue
from wexample_filestate.config_option.content_filter_config_option import ContentFilterConfigOption
from wexample_filestate.operation.file_write_operation import FileWriteOperation
from wexample_filestate.enum.scopes import Scope

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType
    from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class ApplyContentFilterOperation(FileWriteOperation):
    _original_path_str: str

    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.CONTENT

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
        from wexample_filestate.item.item_target_file import ItemTargetFile
        assert isinstance(self.target, ItemTargetFile)
        filters = cast(ContentFilterConfigOption, self.target.get_option(ContentFilterConfigOption)).get_filters()

        self._target_file_write(
            content=ConfigValue.apply_filters(
                content=self.target.get_local_file().read(),
                filters=filters,
            )
        )
