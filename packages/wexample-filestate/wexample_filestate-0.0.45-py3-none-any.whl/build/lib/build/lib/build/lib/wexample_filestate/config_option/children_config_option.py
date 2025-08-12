import os
from typing import Any, cast, Union, Optional, List, TYPE_CHECKING

from wexample_config.config_option.children_config_option import (
    ChildrenConfigOption as BaseChildrenConfigOption,
)
from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.mixin.item_config_option_mixin import ItemTreeConfigOptionMixin
from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType

if TYPE_CHECKING:
    from pip.prompt.wexample_prompt.common.io_manager import IoManager


class ChildrenConfigOption(ItemTreeConfigOptionMixin, BaseChildrenConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        from wexample_filestate.config_option.abstract_children_manipulator_config_option import \
            AbstractChildrenManipulationConfigOption
        return list[Union[dict[str, Any], AbstractChildrenManipulationConfigOption]]

    def get_parent(self) -> "TargetFileOrDirectoryType":
        assert self.parent is not None
        return cast("TargetFileOrDirectory", self.parent)

    def set_value(self, raw_value: Any):
        from wexample_config.config_option.abstract_config_option import (
            AbstractConfigOption,
        )

        # Ignore default children class set_value
        AbstractConfigOption.set_value(self, raw_value)

    def build_item_tree(self):
        super().build_item_tree()
        children = self.create_children_items()

        # Continue item tree.
        for child in children:
            child.build_item_tree()

    def create_children_items(self) -> List["TargetFileOrDirectoryType"]:
        from wexample_filestate.config_option.abstract_children_manipulator_config_option import \
            AbstractChildrenManipulationConfigOption

        children = []
        # Parent item should be a file or directory target.
        for child_config in self.get_value().get_list():
            if isinstance(child_config, AbstractChildrenManipulationConfigOption):
                child = child_config
                # Parent has not been assigned before now.
                child.parent = self

                children.extend(child.generate_children())

            else:
                children.append(self.create_child_item(
                    child_config=child_config
                ))

        self.children = children
        return children

    def create_child_item(
        self,
        child_config: DictConfig,
        item_name: Optional[str] = None
    ) -> "TargetFileOrDirectoryType":
        from wexample_filestate.const.disk import DiskItemType
        from wexample_filestate.helpers.config_helper import config_is_item_type
        from wexample_filestate.item.item_target_directory import ItemTargetDirectory
        from wexample_filestate.item.item_target_file import ItemTargetFile

        if "class" in child_config:
            class_name = child_config.get("class")

            if not issubclass(
                class_name, ItemTargetDirectory
            ) and not issubclass(
                child_config.get("class"), ItemTargetFile
            ):
                from wexample_filestate.exception.config import (
                    BadConfigurationClassTypeException,
                )

                raise BadConfigurationClassTypeException(
                    f"Class {child_config['class'].__name__} option "
                    f"should extend {ItemTargetDirectory.__name__} "
                    f"or {ItemTargetFile.__name__}"
                )

            child = class_name(
                io=self.get_io(),
                # Name might be not mandatory when using custom class
                config=child_config,
                parent=self,
            )
        else:
            is_file_type = config_is_item_type(child_config, DiskItemType.FILE)
            if not is_file_type:
                name = item_name or child_config.get("name", None)
                if name:
                    # The current item has a parent, so we can try to guess the file type.
                    is_file_type = isinstance(name, str) and os.path.isfile(
                        os.path.join(self.get_parent_item().get_resolved(), name)
                    )

            if is_file_type:
                child = ItemTargetFile(
                    io=self.get_io(),
                    parent=self,
                )
            else:
                child = ItemTargetDirectory(
                    io=self.get_io(),
                    parent=self,
                )

        child.configure(child_config)
        return child

    def get_children(self) -> list[TargetFileOrDirectoryType]:
        return cast(list[TargetFileOrDirectoryType], self.children)

    def get_io(self) -> "IoManager":
        return self.get_parent_item().io
