from typing import TYPE_CHECKING, List, Type

from wexample_filestate.operation.apply_content_filter_operation import ApplyContentFilterOperation
from wexample_filestate.operations_provider.abstract_operations_provider import (
    AbstractOperationsProvider,
)

if TYPE_CHECKING:
    from wexample_filestate.operation.abstract_operation import AbstractOperation


class DefaultOperationsProvider(AbstractOperationsProvider):
    @staticmethod
    def get_operations() -> List[Type["AbstractOperation"]]:
        from wexample_filestate.operation.file_create_operation import (
            FileCreateOperation,
        )
        from wexample_filestate.operation.file_remove_operation import (
            FileRemoveOperation,
        )
        from wexample_filestate.operation.file_write_operation import FileWriteOperation
        from wexample_filestate.operation.file_change_extension_operation import FileChangeExtensionOperation
        from wexample_filestate.operation.item_change_mode_operation import (
            ItemChangeModeOperation,
        )

        return [
            ApplyContentFilterOperation,
            FileChangeExtensionOperation,
            FileCreateOperation,
            FileRemoveOperation,
            FileWriteOperation,
            ItemChangeModeOperation,
        ]
