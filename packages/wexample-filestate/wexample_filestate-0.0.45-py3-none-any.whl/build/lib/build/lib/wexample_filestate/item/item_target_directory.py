from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Type, cast

from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.mixin.item_config_option_mixin import ItemTreeConfigOptionMixin
from wexample_filestate.item.abstract_item_target import AbstractItemTarget
from wexample_filestate.item.mixins.item_directory_mixin import ItemDirectoryMixin
from wexample_helpers.const.types import FileStringOrPath
from wexample_prompt.common.io_manager import IoManager

if TYPE_CHECKING:
    from wexample_config.options_provider.abstract_options_provider import (
        AbstractOptionsProvider,
    )
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType
    from wexample_filestate.operations_provider.abstract_operations_provider import (
        AbstractOperationsProvider,
    )
    from wexample_filestate.result.abstract_result import AbstractResult
    from wexample_filestate.result.file_state_dry_run_result import (
        FileStateDryRunResult,
    )
    from wexample_filestate.result.file_state_result import FileStateResult


class ItemTargetDirectory(ItemDirectoryMixin, AbstractItemTarget):
    last_result: AbstractResult | None = None

    def __init__(self, **kwargs):
        # Initialize ItemDirectoryMixin first to prevent Pydantic from resetting
        # attributes during AbstractItemTarget initialization.
        # The order matters here because Pydantic's model initialization
        # can override attributes set by previous parent classes.
        ItemDirectoryMixin.__init__(self, **kwargs)
        AbstractItemTarget.__init__(self, **kwargs)

    def build_item_tree(self) -> None:
        super().build_item_tree()

        for option in self.options.values():
            if isinstance(option, ItemTreeConfigOptionMixin):
                option.build_item_tree()

    def configure_from_file(self, path: FileStringOrPath):
        from wexample_helpers_yaml.helpers.yaml_helpers import yaml_read

        if yaml_read is not None:
            self.set_value(raw_value=yaml_read(str(path)))

    def get_children_list(self) -> list["TargetFileOrDirectoryType"]:
        from wexample_filestate.config_option.children_config_option import (
            ChildrenConfigOption,
        )

        option = cast(ChildrenConfigOption, self.get_option(ChildrenConfigOption))
        if option is not None:
            return option.get_children()

        return []

    def build_operations(self, result: "AbstractResult"):
        from wexample_filestate.const.state_items import TargetFileOrDirectory
        super().build_operations(result)

        for item in self.get_children_list():
            cast(TargetFileOrDirectory, item).build_operations(result)

    def find_by_path_recursive(self, path: Path) -> Optional["TargetFileOrDirectoryType"]:
        found = self.find_by_path(path)
        if found:
            return found

        for child in self.get_children_list():
            if child.is_directory():
                result = cast(
                    ItemTargetDirectory, child
                ).find_by_path_recursive(path)
                if result:
                    return result

        return None

    def find_by_path(self, path: Path) -> Optional["TargetFileOrDirectoryType"]:
        path_str = str(path.resolve())

        for child in self.get_children_list():
            if str(child.get_resolved()) == path_str:
                return child

        return None

    def find_by_name_recursive(self, item_name: str) -> Optional["TargetFileOrDirectoryType"]:
        found = self.find_by_name(item_name)
        if found:
            return found

        for child in self.get_children_list():
            if child.is_directory():
                result = cast(
                    ItemTargetDirectory, child
                ).find_by_name_recursive(item_name)
                if result:
                    return result

        return None

    def find_by_name(self, item_name: str) -> Optional["TargetFileOrDirectoryType"]:
        for child in self.get_children_list():
            if child.get_item_name() == item_name:
                return child

        return None

    def find_by_name_or_fail(self, item_name: str) -> "TargetFileOrDirectoryType":
        child = self.find_by_name(item_name)
        if child is None:
            from wexample_filestate.exception.item import ChildNotFoundException

            raise ChildNotFoundException(f"Child not found: {item_name}")

        return child

    def rollback(self) -> "FileStateResult":
        from wexample_filestate.result.file_state_result import FileStateResult

        result = FileStateResult(state_manager=self, rollback=True)

        # Fetch applied operations to a new stack.
        if self.last_result:
            for operation in self.last_result.operations:
                if operation.applied:
                    result.operations.append(operation)

        result.apply_operations()
        self.last_result = result

        return result

    def run(self, result: "AbstractResult") -> "AbstractResult":
        self.build_operations(result)
        self.last_result = result

        return self.last_result

    def dry_run(self) -> "FileStateDryRunResult":
        from wexample_filestate.result.file_state_dry_run_result import (
            FileStateDryRunResult,
        )

        return cast(
            FileStateDryRunResult, self.run(FileStateDryRunResult(state_manager=self))
        )

    def apply(self) -> "FileStateResult":
        from wexample_filestate.result.file_state_result import FileStateResult

        result = cast(FileStateResult, self.run(FileStateResult(state_manager=self)))
        result.apply_operations()

        return result

    @classmethod
    def create_from_path(
        cls,
        path: str,
        config: Optional[DictConfig] = None,
        io_manager: Optional[IoManager] = None,
        options_providers: Optional[List[Type["AbstractOptionsProvider"]]] = None,
        operations_providers: Optional[List[Type["AbstractOperationsProvider"]]] = None,
    ) -> "ItemTargetDirectory":
        import os

        from wexample_helpers.helpers.directory import (
            directory_get_base_name,
            directory_get_parent_path,
        )

        config = config or {}

        # If path is a file, ignore file name a keep parent directory.
        if os.path.isfile(path):
            path = os.path.dirname(path)

        manager = cls(
            base_path=directory_get_parent_path(path),
            io=io_manager or IoManager(),
            options_providers=options_providers,
            operations_providers=operations_providers,
        )

        config["name"] = config["name"] if config.get("name") else directory_get_base_name(path)
        manager.configure(config=config)
        return manager
