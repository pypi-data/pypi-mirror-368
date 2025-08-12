from typing import Any, Union

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.const.files import FileSystemPermission


class ModeRecursiveConfigOption(AbstractConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Union[bool, FileSystemPermission]
