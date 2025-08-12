from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from wexample_config.const.types import DictConfig
from wexample_filestate.testing.abstract_state_manager_test import AbstractStateManagerTest

if TYPE_CHECKING:
    from wexample_filestate.result.file_state_dry_run_result import (
        FileStateDryRunResult,
    )


class TestAbstractOperation(AbstractStateManagerTest, ABC):
    def test_apply(self) -> None:
        self._operation_test_setup()
        self._operation_test_assert_initial()
        self._operation_test_dry_run()
        self._operation_test_apply()
        self._operation_test_assert_applied()
        self._operation_test_rollback()
        self._operation_test_assert_rollback()

    def _dry_run_and_count_operations(self) -> "FileStateDryRunResult":
        result = self.state_manager.dry_run()

        operations_count = self._operation_get_count()
        assert len(result.operations) == operations_count

        return result

    def _operation_get_count(self) -> int:
        return 1

    def _operation_test_setup(self) -> None:
        config = self._operation_test_setup_configuration()

        if config is not None:
            self.state_manager.configure(config=config)

    def _operation_test_setup_configuration(self) -> Optional[DictConfig]:
        return None

    def _operation_test_assert_initial(self) -> None:
        pass

    def _operation_test_dry_run(self) -> None:
        self._dry_run_and_count_operations()

    def _operation_test_apply(self) -> None:
        self.state_manager.apply()

    @abstractmethod
    def _operation_test_assert_applied(self) -> None:
        pass

    def _operation_test_rollback(self) -> None:
        self.state_manager.rollback()

    def _operation_test_assert_rollback(self):
        # Rerun initial checkup
        self._operation_test_assert_initial()
