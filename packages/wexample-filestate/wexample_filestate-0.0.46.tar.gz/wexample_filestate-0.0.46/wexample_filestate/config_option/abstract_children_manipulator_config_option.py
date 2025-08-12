from abc import abstractmethod
from pathlib import Path
from typing import Any, TYPE_CHECKING, List, cast

from wexample_config.config_option.abstract_nested_config_option import AbstractNestedConfigOption
from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.mixin.item_config_option_mixin import ItemTreeConfigOptionMixin

if TYPE_CHECKING:
    from wexample_config.options_provider.abstract_options_provider import AbstractOptionsProvider
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType


class AbstractChildrenManipulationConfigOption(ItemTreeConfigOptionMixin, AbstractNestedConfigOption):
    pattern: DictConfig

    def get_options_providers(self) -> list[type["AbstractOptionsProvider"]]:
        from wexample_filestate.options_provider.default_options_provider import DefaultOptionsProvider

        return [
            DefaultOptionsProvider,
        ]

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return DictConfig

    @abstractmethod
    def generate_children(self) -> List["TargetFileOrDirectoryType"]:
        pass

    def _path_match_patterns(self, path: str):
        import re
        from wexample_filestate.config_option.name_pattern_config_option import NamePatternConfigOption

        config = self.pattern
        option_name = NamePatternConfigOption.get_name()
        if config.get(option_name) is None:
            return True

        patterns = config[option_name]

        if isinstance(patterns, str):
            patterns = [patterns]

        for pattern_str in patterns:
            pattern = re.compile(pattern_str)
            if not pattern.match(Path(path).name):
                return False

        return True

    def _create_children_from_config(self, path: Path, config: dict) -> "TargetFileOrDirectoryType":
        import copy
        from wexample_filestate.config_option.children_config_option import ChildrenConfigOption

        item_config_copy = copy.deepcopy(config)

        if item_config_copy.get("name", None) is None:
            item_config_copy["name"] = path.name

        parent_children_config = cast(ChildrenConfigOption, self.get_parent())

        return parent_children_config.create_child_item(
            child_config=item_config_copy,
        )

    def _get_directories_filtered(self, base_path: str, recursive: bool = False) -> List[str]:
        from wexample_helpers.helpers.file import file_get_directories

        output = []
        directories = file_get_directories(
            path=base_path
        )

        for directory in directories:
            if self._path_match_patterns(directory):
                output.append(directory)

                if recursive is True:
                    output.extend(
                        self._get_directories_filtered(
                            base_path=directory,
                            recursive=recursive
                        )
                    )

        return output
