from typing import Optional, TYPE_CHECKING

from wexample_filestate.enum.scopes import Scope
from wexample_filestate.file_state_manager import FileStateManager

if TYPE_CHECKING:
    from wexample_prompt.common.io_manager import IoManager
    from wexample_config.const.types import DictConfig


class WithWorkdirMixin:
    workdir: FileStateManager = None
    host_workdir: FileStateManager = None

    def _init_workdir(
            self,
            entrypoint_path: str,
            io_manager: "IoManager",
            config: Optional["DictConfig"] = None
    ) -> None:
        import os

        self.workdir = self._get_workdir_state_manager_class(
            entrypoint_path=entrypoint_path,
            io_manager=io_manager,
            config=config,
        )

        # Ensure files state, but not content at this point.
        self.workdir.apply(scopes={
            Scope.LOCATION,
            Scope.NAME,
            Scope.OWNERSHIP,
            Scope.PERMISSIONS,
            Scope.SYMLINK_TARGET,
            Scope.TIMESTAMPS,
        })

        # The calling workdir may be in a virtual env host system.
        self.host_workdir = FileStateManager.create_from_path(
            path=os.getcwd(),
            io=io_manager
        )

    def _rebuild_workdir_content(self):
        self.workdir.apply(scopes={
            Scope.CONTENT,
        })

    def _get_workdir_state_manager_class(
            self,
            entrypoint_path: str,
            io_manager: "IoManager",
            config: Optional["DictConfig"] = None
    ) -> FileStateManager:
        return FileStateManager.create_from_path(
            path=entrypoint_path,
            config=config or {},
            io=io_manager
        )
