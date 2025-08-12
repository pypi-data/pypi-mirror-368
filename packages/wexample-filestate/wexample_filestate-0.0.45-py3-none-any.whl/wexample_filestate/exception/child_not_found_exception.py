from typing import TYPE_CHECKING, Optional

from wexample_helpers.exception.undefined_exception import UndefinedException

if TYPE_CHECKING:
    from wexample_filestate.item.abstract_item_target import AbstractItemTarget


class ChildNotFoundException(UndefinedException):
    error_code: str = "FILE_STATE_CHILD_NOT_FOUND"

    def __init__(
            self,
            child: str,
            root_item: Optional["AbstractItemTarget"] = None,
            **kwargs
    ):
        context = (
            f" in {root_item.get_item_title()} '{root_item.get_item_name()}'"
            if root_item is not None else ""
        )
        super().__init__(
            message=f"Child '{child}' not found{context}.",
            **kwargs
        )
