from typing import Any

from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class ShouldExistConfigOption(AbstractConfigOption):
    def __init__(self, value: Any = None, **data) -> None:
        super().__init__(
            # Default is true when class is passed to a set of config.
            value=value if value is not None else True,
            **data
        )

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return bool
