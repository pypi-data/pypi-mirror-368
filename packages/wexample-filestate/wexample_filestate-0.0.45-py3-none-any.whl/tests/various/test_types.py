from typing import Type, Any, Union

from wexample_filestate.item.item_target_directory import ItemTargetDirectory
from wexample_helpers.helpers.polyfill import polyfill_register_global
from wexample_helpers.test.abstract_test_helpers import AbstractTestHelpers


class TestFileStateManager(AbstractTestHelpers):
    def test_types(self):
        from wexample_filestate.file_state_manager import FileStateManager
        from wexample_filestate.config_option.children_filter_config_option import ChildrenFilterConfigOption
        from wexample_filestate.result.abstract_result import AbstractResult

        polyfill_register_global(AbstractResult)

        class TestClass(FileStateManager):
            pass

        self._test_type_validate_or_fail(
            success_cases=[
                (TestClass, Type[ItemTargetDirectory]),
                ([ChildrenFilterConfigOption(pattern={})], list[ChildrenFilterConfigOption]),
                ([ChildrenFilterConfigOption(pattern={})], list[Union[dict[str, Any], ChildrenFilterConfigOption]])
            ]
        )
