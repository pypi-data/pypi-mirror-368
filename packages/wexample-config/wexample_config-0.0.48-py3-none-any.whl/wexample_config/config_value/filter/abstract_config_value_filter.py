from abc import ABC

from pydantic import BaseModel

from wexample_helpers.classes.mixin.has_snake_short_class_name_class_mixin import HasSnakeShortClassNameClassMixin


class AbstractConfigValueFilter(HasSnakeShortClassNameClassMixin, BaseModel, ABC):
    @staticmethod
    def apply_filter(content: str) -> str:
        pass
