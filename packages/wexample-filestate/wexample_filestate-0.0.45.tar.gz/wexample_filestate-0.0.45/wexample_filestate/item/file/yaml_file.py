from typing import Optional, ClassVar

from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.should_have_extension_config_option import ShouldHaveExtensionConfigOption
from wexample_filestate.item.file.structured_content_file import StructuredContentFile
from wexample_helpers.const.types import StructuredData
from wexample_helpers_yaml.const.types import YamlContent


class YamlFile(StructuredContentFile):
    EXTENSION_YAML: ClassVar[str] = "yaml"
    EXTENSION_YML: ClassVar[str] = "yml"

    def _expected_file_name_extension(self) -> str:
        return self.EXTENSION_YML

    def _parse_file_content(self, content: str) -> YamlContent:
        import yaml
        return yaml.safe_load(content)

    def _prepare_content_to_write(self, content: StructuredData) -> str:
        import yaml
        return yaml.dump(content)

    def prepare_value(self, raw_value: Optional[DictConfig] = None) -> DictConfig:
        config = super().prepare_value(
            raw_value=raw_value
        )

        config[ShouldHaveExtensionConfigOption.get_snake_short_class_name()] = self._expected_file_name_extension()

        return config
