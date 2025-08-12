from typing import Any, Union

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.const.disk import DiskItemType


class TypeConfigOption(AbstractConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Union[str, DiskItemType]
