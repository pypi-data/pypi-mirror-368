from __future__ import annotations

from wexample_filestate.item.mixins.item_mixin import ItemMixin


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
