from __future__ import annotations

from types import UnionType
from typing import TYPE_CHECKING, Any, List, Type

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_config.config_option.abstract_nested_config_option import AbstractNestedConfigOption

if TYPE_CHECKING:
    pass


class AbstractListConfigOption(AbstractNestedConfigOption):
    children: List[AbstractConfigOption] = []

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return List[dict[str, Any]]

    @staticmethod
    def get_allowed_types() -> Type | UnionType:
        return List[dict[str, Any]]

    def get_item_class_type(self):
        return AbstractConfigOption

    def set_value(self, raw_value: Any) -> None:
        # Skip direct parent which creates only one item.
        AbstractConfigOption.set_value(self, raw_value)

        if raw_value is None:
            return

        for child_config in raw_value:
            self.children.append(
                self.get_item_class_type()(
                    value=child_config,
                    parent=self
                )
            )
