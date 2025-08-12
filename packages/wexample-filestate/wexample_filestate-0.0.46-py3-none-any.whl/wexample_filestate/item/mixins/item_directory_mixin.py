from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.item.mixins.item_mixin import ItemMixin

if TYPE_CHECKING:
    from wexample_file.common.local_directory import LocalDirectory


class ItemDirectoryMixin(ItemMixin):
    def get_item_title(self) -> str:
        return "Directory"

    def get_resolved(self) -> str:
        import os

        return f"{super().get_resolved()}{os.sep}"

    def is_file(self) -> bool:
        return False

    def is_directory(self) -> bool:
        return True

    def get_local_directory(self) -> "LocalDirectory":
        from wexample_file.common.local_directory import LocalDirectory
        return LocalDirectory(path=self.get_path())
