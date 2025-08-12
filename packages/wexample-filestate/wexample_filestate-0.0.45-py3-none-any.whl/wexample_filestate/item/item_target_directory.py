from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, cast, Set

from pydantic import Field

from wexample_filestate.config_option.mixin.item_config_option_mixin import ItemTreeConfigOptionMixin
from wexample_filestate.item.abstract_item_target import AbstractItemTarget
from wexample_filestate.item.mixins.item_directory_mixin import ItemDirectoryMixin
from wexample_helpers.const.types import FileStringOrPath
from wexample_helpers.const.types import StringKeysDict
from wexample_filestate.enum.scopes import Scope

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType
    from wexample_filestate.result.abstract_result import AbstractResult


class ItemTargetDirectory(ItemDirectoryMixin, AbstractItemTarget):
    shortcuts: StringKeysDict = Field(default_factory=dict)

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

    def build_operations(self, result: "AbstractResult", scopes: Optional[Set[Scope]] = None):
        from wexample_filestate.const.state_items import TargetFileOrDirectory
        super().build_operations(result, scopes=scopes)

        for item in self.get_children_list():
            cast(TargetFileOrDirectory, item).build_operations(
                result=result,
                scopes=scopes
            )

    def find_by_path_recursive(self, path: FileStringOrPath) -> Optional["TargetFileOrDirectoryType"]:
        path = Path(path)
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

    def find_by_path(self, path: FileStringOrPath) -> Optional["TargetFileOrDirectoryType"]:
        path_str = str(Path(path).resolve())

        for child in self.get_children_list():
            if child.get_resolved() == path_str:
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
            from wexample_filestate.exception.child_not_found_exception import ChildNotFoundException

            raise ChildNotFoundException(
                child=item_name,
                root_item=self
            )

        return child

    def get_shortcut(self, name: str) -> Optional["AbstractItemTarget"]:
        return self.shortcuts[name] if name in self.shortcuts else None

    def get_shortcut_or_fail(self, name: str) -> Optional["AbstractItemTarget"]:
        shortcut = self.get_shortcut(name=name)

        if shortcut is None:
            from wexample_filestate.exception.undefined_shortcut_exception import UndefinedShortcutException

            raise UndefinedShortcutException(
                shortcut=name,
                root_item=self
            )

    def set_shortcut(self, name: str, children: "AbstractItemTarget"):
        if name in self.shortcuts:
            from wexample_filestate.exception.existing_shortcut_exception import ExistingShortcutException

            raise ExistingShortcutException(
                shortcut=name,
                new_item=children,
                existing_item=self.shortcuts[name],
                root_item=self
            )

        self.shortcuts[name] = children

    @classmethod
    def create_from_path(
            cls,
            path: str,
            **kwargs
    ) -> "ItemTargetDirectory":
        # If path is a file, ignore file name a keep parent directory.
        path = Path(path)
        if path.is_file():
            path = path.parent

        return super().create_from_path(
            path=path,
            **kwargs
        )
