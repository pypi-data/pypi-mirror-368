import os
from abc import ABC
from typing import TYPE_CHECKING, List, Optional, Type, cast

if TYPE_CHECKING:
    from wexample_config.options_provider.abstract_options_provider import (
        AbstractOptionsProvider,
    )
    from wexample_filestate.file_state_manager import FileStateManager
    from wexample_filestate.operations_provider.abstract_operations_provider import (
        AbstractOperationsProvider,
    )


class AbstractStateManagerTest(ABC):
    state_manager: "FileStateManager"

    def _get_package_root_path(self) -> str:
        return f"{os.path.abspath(os.curdir)}{os.sep}"

    def _get_test_state_manager_path(self, package_root_path: Optional[str] = None) -> str:
        return os.path.join(package_root_path or self._get_package_root_path(), "tests", "resources", "")

    def _get_absolute_path_from_state_manager(self, relative: str) -> str:
        return os.path.join(self._get_test_state_manager_path(), relative)

    def setup_method(self) -> None:
        from wexample_filestate.file_state_manager import FileStateManager

        self.state_manager = cast(
            FileStateManager,
            self._get_test_manager_class().create_from_path(
                path=self._get_test_state_manager_path(),
                options_providers=self._get_test_options_providers(),
                operations_providers=self._get_test_operations_providers(),
            ),
        )

    def _get_test_manager_class(self):
        from wexample_filestate.file_state_manager import FileStateManager

        return FileStateManager

    def _get_test_operations_providers(
        self,
    ) -> Optional[List[Type["AbstractOperationsProvider"]]]:
        return None

    def _get_test_options_providers(
        self,
    ) -> Optional[List[Type["AbstractOptionsProvider"]]]:
        return None

    def _assert_file_content_equals(
        self, file_path: str, expected_value: str, positive: bool = True
    ):
        from wexample_helpers.helpers.file import file_read

        assert (file_read(file_path) == expected_value) == positive

    def _assert_dir_exists(self, dir_path: str, positive: bool = True):
        assert (os.path.isdir(dir_path)) == positive

    def _assert_file_exists(self, file_path: str, positive: bool = True):
        assert (os.path.isfile(file_path)) == positive

    def _assert_state_manager_target_directory_exists(
        self, item_name: str, positive: bool = True
    ) -> None:
        target = self.state_manager.find_by_name_or_fail(item_name)

        # Target should always exist
        assert target is not None
        self._assert_dir_exists(target.get_resolved(), positive=positive)
