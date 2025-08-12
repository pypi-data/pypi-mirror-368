from typing import Any, Union, Type

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_config.config_value.filter.abstract_config_value_filter import AbstractConfigValueFilter


class ContentFilterConfigOption(AbstractConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Union[list[Type[AbstractConfigValueFilter]], Type[AbstractConfigValueFilter]]

    def get_filters(self) -> list[AbstractConfigValueFilter]:
        value = self.get_value().get_class()
        return value if isinstance(value, list) else [value]

    def dump(self) -> Any:
        filters_names = []

        for content_filter in self.get_filters():
            filters_names.append(content_filter.get_name())

        return f"filters=[','.join(filters_names)]"
