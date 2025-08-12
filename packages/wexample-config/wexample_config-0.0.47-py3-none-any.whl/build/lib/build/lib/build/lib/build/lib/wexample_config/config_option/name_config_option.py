from typing import Any, Union, Callable

from wexample_config.config_option.abstract_config_option import AbstractConfigOption
from wexample_config.config_value.callback_render_config_value import (
    CallbackRenderConfigValue,
)
from wexample_config.const.types import DictConfig


class NameConfigOption(AbstractConfigOption):
    @staticmethod
    def get_raw_value_allowed_type() -> Any:
        return Union[str, CallbackRenderConfigValue, Callable[..., Any]]

    @staticmethod
    def resolve_config(config: DictConfig) -> DictConfig:
        key = NameConfigOption.get_name()

        if key in config:
            value = config.get(key)

            if callable(value):
                config[key] = CallbackRenderConfigValue(raw=value)

        return config
