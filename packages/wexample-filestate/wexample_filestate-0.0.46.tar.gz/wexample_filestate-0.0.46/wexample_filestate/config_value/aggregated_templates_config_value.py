import os
from typing import Dict, Optional, List, Any

from wexample_config.config_value.config_value import ConfigValue
from wexample_helpers.const.types import BasicValue
from wexample_helpers.helpers.string import string_replace_params


class AggregatedTemplatesConfigValue(ConfigValue):
    raw: Any = None
    templates: Optional[List[str]] = []
    parameters: Optional[Dict[str, BasicValue]] = {}

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Any

    def get_templates(self) -> Optional[List[str]]:
        return self.templates

    def get_str(self, type_check: bool = True) -> str:
        output = []

        for template_content in self.get_templates():
            output.append(string_replace_params(template_content, self.parameters))

        output_str = os.linesep.join(output)
        self.set_str(output_str)

        return output_str
