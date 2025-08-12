from typing import Optional, List

from wexample_filestate.config_value.aggregated_templates_config_value import AggregatedTemplatesConfigValue


class ReadmeContentConfigValue(AggregatedTemplatesConfigValue):

    def get_templates(self) -> Optional[List[str]]:
        return [
            '## Introduction',
            '## License'
        ]
