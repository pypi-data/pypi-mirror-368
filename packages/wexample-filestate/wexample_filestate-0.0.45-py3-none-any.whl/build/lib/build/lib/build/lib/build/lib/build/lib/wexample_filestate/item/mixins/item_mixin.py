from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from wexample_helpers.const.types import FileStringOrPath


class ItemMixin(BaseModel):
    base_path: Optional[FileStringOrPath] = None
    path: Optional[Path] = None

    @abstractmethod
    def get_item_title(self) -> str:
        pass

    @abstractmethod
    def is_file(self) -> bool:
        pass

    @abstractmethod
    def is_directory(self) -> bool:
        pass

    def get_octal_mode(self: ItemMixin) -> str:
        from wexample_helpers.helpers.file import file_path_get_octal_mode

        return file_path_get_octal_mode(self.get_path())

    def get_path(self) -> Path:
        assert self.path is not None
        return Path(f"{self.path}")

    def get_path_str(self) -> str:
        return str(self.get_path())

    def get_resolved(self) -> str:
        return str(self.get_path().resolve())
