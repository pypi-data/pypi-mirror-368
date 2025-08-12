from typing import TYPE_CHECKING, List, Type

from wexample_config.options_provider.abstract_options_provider import (
    AbstractOptionsProvider,
)
from wexample_filestate.config_option.children_file_factory_config_option import ChildrenFileFactoryConfigOption
from wexample_filestate.config_option.should_contain_lines_config_option import ShouldContainLinesConfigOption

if TYPE_CHECKING:
    from wexample_config.config_option.abstract_config_option import (
        AbstractConfigOption,
    )


class DefaultOptionsProvider(AbstractOptionsProvider):
    @classmethod
    def get_options(cls) -> List[Type["AbstractConfigOption"]]:
        from wexample_config.config_option.name_config_option import NameConfigOption
        from wexample_filestate.config_option.children_config_option import (
            ChildrenConfigOption,
        )
        from wexample_filestate.config_option.class_config_option import (
            ClassConfigOption,
        )
        from wexample_filestate.config_option.content_config_option import (
            ContentConfigOption,
        )
        from wexample_filestate.config_option.default_content_config_option import (
            DefaultContentConfigOption,
        )
        from wexample_filestate.config_option.mode_config_option import ModeConfigOption
        from wexample_filestate.config_option.mode_recursive_config_option import (
            ModeRecursiveConfigOption,
        )
        from wexample_filestate.config_option.name_pattern_config_option import (
            NamePatternConfigOption,
        )
        from wexample_filestate.config_option.remove_backup_max_file_size_config_option import (
            RemoveBackupMaxFileSizeConfigOption,
        )
        from wexample_filestate.config_option.should_exist_config_option import (
            ShouldExistConfigOption,
        )
        from wexample_filestate.config_option.type_config_option import TypeConfigOption
        from wexample_filestate.config_option.content_filter_config_option import ContentFilterConfigOption

        return [
            ChildrenConfigOption,
            ChildrenFileFactoryConfigOption,
            ClassConfigOption,
            ContentConfigOption,
            ContentFilterConfigOption,
            DefaultContentConfigOption,
            ModeConfigOption,
            ModeRecursiveConfigOption,
            NameConfigOption,
            NamePatternConfigOption,
            RemoveBackupMaxFileSizeConfigOption,
            ShouldContainLinesConfigOption,
            ShouldExistConfigOption,
            TypeConfigOption,
        ]
