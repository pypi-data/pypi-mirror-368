from typing import cast


class RenderableConfigOptionMixin:
    def render_content(self) -> str:
        from wexample_config.config_option.abstract_config_option import (
            AbstractConfigOption,
        )

        return cast(AbstractConfigOption, self).get_value().get_str()
