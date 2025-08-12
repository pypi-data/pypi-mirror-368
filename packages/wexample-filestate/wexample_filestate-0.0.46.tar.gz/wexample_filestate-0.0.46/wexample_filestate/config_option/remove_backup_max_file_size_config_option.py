from typing import Any

from wexample_config.config_option.abstract_config_option import AbstractConfigOption

REMOVE_BACKUP_MAX_FILE_SIZE_DEFAULT: int = 1000


class RemoveBackupMaxFileSizeConfigOption(AbstractConfigOption):
    value: int = REMOVE_BACKUP_MAX_FILE_SIZE_DEFAULT

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return int
