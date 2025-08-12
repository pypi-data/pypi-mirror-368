from wexample_config.config_value.filter.abstract_config_value_filter import AbstractConfigValueFilter


class TrimConfigValueFilter(AbstractConfigValueFilter):
    @staticmethod
    def apply_filter(content: str) -> str:
        return content.strip()
