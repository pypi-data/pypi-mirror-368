from typing import Any, Union

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_filestate.const.files import (
    FileSystemPermission,
)
from wexample_helpers.helpers.file import file_mode_octal_to_num


class ModeConfigOption(AbstractConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Union[str, int, FileSystemPermission]

    def get_octal(self) -> str:
        value = self.get_value()

        if value.is_str():
            return value.get_str()
        elif value.is_int():
            return value.to_str()
        elif value.is_dict():
            value_dict = value.get_dict()
            if value_dict.get("mode"):
                return str(value["mode"])

        raise ValueError(f"Unexpected value in get_octal: {value}")

    def get_int(self) -> int:
        return file_mode_octal_to_num(self.get_octal())
