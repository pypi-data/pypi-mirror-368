from __future__ import annotations

from typing import Any

from wexample_config.config_option.abstract_list_config_option import AbstractListConfigOption
from wexample_config.config_option.abstract_nested_config_option import AbstractNestedConfigOption


class ChildrenConfigOption(AbstractListConfigOption):
    def get_item_class_type(self):
        return AbstractNestedConfigOption

    def dump(self) -> Any:
        output = []

        for child in self.children:
            output.append(child.dump())

        return output
