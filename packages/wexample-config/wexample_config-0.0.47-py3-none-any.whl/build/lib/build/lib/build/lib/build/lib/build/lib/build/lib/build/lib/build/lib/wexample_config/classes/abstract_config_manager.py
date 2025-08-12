from typing import Any

from wexample_config.config_option.abstract_nested_config_option import (
    AbstractNestedConfigOption,
)


class AbstractConfigManager(AbstractNestedConfigOption):
    def __init__(self, value: Any = None, **data) -> None:
        super().__init__(
            value=value,
            **data
        )
