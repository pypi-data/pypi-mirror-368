from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Type, cast, Any

from wexample_config.config_option.abstract_nested_config_option import AbstractNestedConfigOption
from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.mixin.item_config_option_mixin import ItemTreeConfigOptionMixin
from wexample_filestate.item.mixins.item_mixin import ItemMixin
from wexample_prompt.mixins.with_required_io_manager import WithRequiredIoManager
from wexample_filestate.operations_provider.abstract_operations_provider import (
    AbstractOperationsProvider,
)

if TYPE_CHECKING:
    from wexample_config.options_provider.abstract_options_provider import (
        AbstractOptionsProvider,
    )
    from wexample_filestate.operation.abstract_operation import AbstractOperation
    from wexample_filestate.result.abstract_result import AbstractResult
    from wexample_filestate.const.types_state_items import SourceFileOrDirectoryType
    from wexample_filestate.const.state_items import SourceFileOrDirectory
    from wexample_prompt.common.io_manager import IoManager


class AbstractItemTarget(WithRequiredIoManager, ItemMixin, ItemTreeConfigOptionMixin, AbstractNestedConfigOption, ABC):
    source: Optional["SourceFileOrDirectory"] = None
    operations_providers: Optional[List[Type[AbstractOperationsProvider]]] = None

    def __init__(self, io:"IoManager", **kwargs):
        ItemMixin.__init__(self, **kwargs)
        AbstractNestedConfigOption.__init__(self, **kwargs)
        WithRequiredIoManager.__init__(self, io=io)

    def configure(self, config: DictConfig):
        self.set_value(raw_value=config)
        self.locate_source(self.get_path())


    def locate_source(self, path: Path) -> "SourceFileOrDirectoryType":
        if path.is_file():
            from wexample_filestate.item.item_source_file import ItemSourceFile
            self.source = ItemSourceFile(
                path=path,
            )
        elif path.is_dir():
            from wexample_filestate.item.item_source_directory import ItemSourceDirectory
            self.source = ItemSourceDirectory(
                path=path,
            )

        return self.source

    def get_path(self) -> Path:
        # Base path is specified, for instance for the tree root.
        if self.base_path is not None:
            base_path = self.base_path
        else:
            base_path = self.get_parent_item().get_resolved()

        return Path(f"{base_path}{self.get_item_name()}")

    def get_operations(self) -> List[Type["AbstractOperation"]]:
        providers = self.get_operations_providers()
        operations = []

        for provider in providers:
            operations.extend(
                cast("AbstractOperationsProvider", provider).get_operations()
            )

        return operations

    def get_options_providers(self) -> List[Type["AbstractOptionsProvider"]]:
        providers = super().get_options_providers()
        if len(providers) > 0:
            return providers

        from wexample_filestate.options_provider.default_options_provider import (
            DefaultOptionsProvider,
        )

        return [
            DefaultOptionsProvider,
        ]

    def build_operations(self, result: "AbstractResult"):
        from wexample_filestate.const.types_state_items import TargetFileOrDirectoryType

        for operation_class in self.get_operations():
            self_casted = cast(TargetFileOrDirectoryType, self)
            if operation_class.applicable(self_casted):
                result.operations.append(operation_class(
                    io=self.io,
                    target=self_casted
                ))

    def get_operations_providers(self) -> List[Type["AbstractOperationsProvider"]]:
        if self.parent:
            return cast(AbstractItemTarget, self.get_parent_item()).get_operations_providers()

        if self.operations_providers:
            return self.operations_providers

        from wexample_filestate.operations_provider.default_operations_provider import (
            DefaultOperationsProvider,
        )

        return [
            DefaultOperationsProvider,
        ]

    def get_item_name(self) -> str:
        from wexample_config.config_option.name_config_option import NameConfigOption
        return self.get_option(NameConfigOption).get_value().get_str()

    def get_source(self) -> "SourceFileOrDirectory":
        assert self.source is not None
        return self.source

    def dump(self) -> Any:
        output = super().dump()
        output["name"] = self.get_item_name()

        return output

    def print_dump(self, pretty: bool = True) -> None:
            from pprint import pprint
            pprint(self.dump(), indent=2)
