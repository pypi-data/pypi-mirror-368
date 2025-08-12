from typing import Any

from wexample_config.config_option.abstract_config_option import AbstractConfigOption


class DemoExtensibleConfigOption(AbstractConfigOption):
    allow_undefined_keys: bool = True

    @staticmethod
    def get_allowed_types() -> Any:
        return list
