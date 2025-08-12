import os
from typing import Optional

from wexample_config.const.types import DictConfig
from wexample_filestate.const.test import TEST_FILE_NAME_SIMPLE_TEXT
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation


class TestFileCreateFromClassOperation(TestAbstractOperation):
    missing_file_name: str = 'simple-readme.md'

    def _operation_test_setup_configuration(self) -> Optional[DictConfig]:
        from wexample_filestate.file_state_manager import FileStateManager
        from typing import Optional
        from wexample_config.const.types import DictConfig

        class TestClassForTestFileCreateFromClassOperation(FileStateManager):
            def prepare_value(self, config: Optional[DictConfig] = None) -> DictConfig:
                config.update({
                    'children': [
                        {
                            'name': TEST_FILE_NAME_SIMPLE_TEXT,
                            'should_exist': True,
                            # Use string instead of enum to test support
                            "type": "file",
                            'default_content': "TEST_CUSTOM_CLASS"
                        }
                    ]
                })

                return config

        return {
            "children": [
                {
                    "name": "test_class_handler",
                    "should_exist": True,
                    # Use string instead of enum to test support
                    "type": "dir",
                    "class": TestClassForTestFileCreateFromClassOperation,
                }
            ]
        }

    def _operation_get_count(self) -> int:
        return 2

    def _operation_test_assert_initial(self) -> None:
        target_file = self.state_manager.find_by_name_or_fail("test_class_handler")

        assert not os.path.exists(target_file.get_resolved()), "The file should not exist"

    def _operation_test_assert_applied(self):
        target_file = self.state_manager.find_by_name_or_fail("test_class_handler")

        assert os.path.exists(target_file.get_resolved()), "The target file should have been created"
