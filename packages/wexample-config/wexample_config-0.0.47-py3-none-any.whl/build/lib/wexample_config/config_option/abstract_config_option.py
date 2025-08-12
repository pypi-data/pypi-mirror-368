from abc import ABC
from typing import Any, Optional

from pydantic import BaseModel

from wexample_config.config_value.config_value import ConfigValue
from wexample_config.const.types import DictConfig
from wexample_helpers.classes.mixin.has_simple_repr_mixin import HasSimpleReprMixin
from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import (
    HasSnakeShortClassNameClassMixin,
)


class AbstractConfigOption(HasSnakeShortClassNameClassMixin, HasSimpleReprMixin, BaseModel, ABC):
    parent: Optional["AbstractConfigOption"] = None
    config_value: Optional[ConfigValue] = None
    key: Optional[str] = None

    def __init__(self, value: Any = None, **data) -> None:
        super().__init__(**data)

        self.key = self.key or self.get_name()
        self.set_value(value)

    def get_key(self) -> str:
        assert self.key is not None
        return self.key

    def set_value(self, raw_value: Any) -> Any:
        if raw_value is None:
            return

        raw_value = self.prepare_value(raw_value)
        config_value_class = self.get_value_class_type()

        # Check if value is valid for the config option,
        # reuse same method to validate types.
        config_value_class.validate_value_type(
            raw_value=raw_value,
            allowed_type=self.get_raw_value_allowed_type()
        )

        self.config_value = (
            config_value_class(raw=raw_value)
            if not isinstance(raw_value, ConfigValue)
            else raw_value
        )

        return raw_value

    def get_value(self) -> Optional[ConfigValue]:
        return self.config_value

    def prepare_value(self, raw_value: Any) -> Any:
        return raw_value

    def get_value_class_type(self) -> type[ConfigValue]:
        return ConfigValue

    @classmethod
    def get_class_name_suffix(cls) -> Optional[str]:
        return "ConfigOption"

    @staticmethod
    def resolve_config(config: DictConfig) -> DictConfig:
        return config

    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Any

    def dump(self) -> Any:
        return self.get_value().raw

    def get_parent(self) -> "AbstractConfigOption":
        assert self.parent is not None
        return self.parent

    def get_root(self) -> "AbstractConfigOption":
        if self.parent is not None:
            return self.parent.get_root()
        return self
