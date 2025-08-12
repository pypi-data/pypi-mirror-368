from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.item.item_source_file import ItemSourceFile
from wexample_filestate.operation.abstract_operation import AbstractOperation
from wexample_filestate.operation.mixin.file_manipulation_operation_mixin import (
    FileManipulationOperationMixin,
)
from wexample_filestate.enum.scopes import Scope

if TYPE_CHECKING:
    from wexample_filestate.item.item_target_directory import ItemTargetDirectory
    from wexample_filestate.item.item_target_file import ItemTargetFile


class FileChangeExtensionOperation(FileManipulationOperationMixin, AbstractOperation):
    _original_extension: Optional[str] = None

    @classmethod
    def get_scope(cls) -> Scope:
        return Scope.NAME

    @staticmethod
    def applicable_option(
            target: Union["ItemTargetDirectory", "ItemTargetFile"],
            option: "AbstractConfigOption"
    ) -> bool:
        from wexample_filestate.config_option.should_have_extension_config_option import ShouldHaveExtensionConfigOption

        if target.source and target.is_file() and isinstance(option, ShouldHaveExtensionConfigOption):
            assert isinstance(target.source, ItemSourceFile)
            if target.source.get_local_file().get_extension() != option.get_value().get_str():
                return True
        return False

    def describe_before(self) -> str:
        return "HAVE_BAD_EXTENSION"

    def describe_after(self) -> str:
        return "HAVE_PROPER_EXTENSION"

    def description(self) -> str:
        return "Manage file extension by correcting its extension or triggering an error"

    def apply(self) -> None:
        from wexample_filestate.config_option.should_have_extension_config_option import ShouldHaveExtensionConfigOption
        self._original_extension = self.target.get_path().with_suffix("").name

        self.target.get_local_file().change_extension(
            self.target.get_option_value(ShouldHaveExtensionConfigOption).get_str()
        )

    def undo(self) -> None:
        self.target.get_local_file().change_extension(
            self._original_extension
        )

        self._original_extension = None
