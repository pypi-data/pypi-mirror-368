
import os
from pathlib import Path
from typing import TYPE_CHECKING, List

from wexample_filestate.config_option.abstract_children_manipulator_config_option import \
    AbstractChildrenManipulationConfigOption
from wexample_filestate.config_option.name_pattern_config_option import NamePatternConfigOption

if TYPE_CHECKING:
    from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType


class ChildrenFilterConfigOption(AbstractChildrenManipulationConfigOption):
    def generate_children(self) -> List["TargetFileOrDirectoryType"]:
        from wexample_filestate.helpers.config_helper import config_has_same_type_as_file
        config = self.pattern
        children = []

        name_pattern_option_name = NamePatternConfigOption.get_name()
        parent_item = self.get_parent_item()
        if config.get(name_pattern_option_name):
            path = parent_item.get_path()
            if path.exists():
                base_path = parent_item.get_resolved()
                for file in os.listdir(base_path):
                    path = Path(f"{base_path}{file}")
                    if self._path_match_patterns(str(path)):
                        if "type" not in config or config_has_same_type_as_file(config, path):
                            children.append(self._create_children_from_config(path, config))
        return children