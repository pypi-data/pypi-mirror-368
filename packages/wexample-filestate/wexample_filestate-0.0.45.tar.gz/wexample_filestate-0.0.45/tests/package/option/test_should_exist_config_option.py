from typing import Optional, Any

from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation


class TestShouldExistConfigOption(TestAbstractOperation):
    def _operation_test_setup_configuration(self) -> Optional[Any]:
        from wexample_filestate.config_option.should_exist_config_option import ShouldExistConfigOption

        return {
            # Simply test this configuration format.
            ShouldExistConfigOption
        }

    def _operation_get_count(self) -> int:
        return 0
