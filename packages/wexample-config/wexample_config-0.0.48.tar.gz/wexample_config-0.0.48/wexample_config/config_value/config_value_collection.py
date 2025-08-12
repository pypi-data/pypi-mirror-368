from typing import List, TypeVar, Generic, Optional, Any, Iterator, Callable

from pydantic import BaseModel, Field
from wexample_config.config_value.config_value import ConfigValue
from wexample_helpers.const.types import AnyList

T = TypeVar('T')


class ConfigValueCollection(BaseModel, Generic[T]):
    """A collection of ConfigValue objects that provides utility methods for working with collections."""
    items: List[ConfigValue] = Field(
        default_factory=list,
        description="List of ConfigValue objects in the collection."
    )

    def __init__(self, **data) -> None:
        super().__init__(**data)

    def __iter__(self) -> Iterator[ConfigValue]:
        """Allow iteration over the collection items."""
        return iter(self.items)

    def __len__(self) -> int:
        """Return the number of items in the collection."""
        return len(self.items)

    def __getitem__(self, index: int) -> ConfigValue:
        """Allow indexing to access items directly."""
        return self.items[index]

    def append(self, value: ConfigValue) -> None:
        """Add a ConfigValue to the collection."""
        self.items.append(value)

    def extend(self, values: List[ConfigValue]) -> None:
        """Add multiple ConfigValue objects to the collection."""
        self.items.extend(values)

    def map(self, func: Callable[[ConfigValue], T]) -> List[T]:
        """Apply a function to each ConfigValue in the collection and return the results."""
        return [func(item) for item in self.items]

    # Collection conversion methods
    def get_str_collection(self) -> List[str]:
        """Convert all items in the collection to strings."""
        return self.map(lambda item: item.get_str())

    def get_int_collection(self) -> List[int]:
        """Convert all items in the collection to integers."""
        return self.map(lambda item: item.get_int())

    def get_float_collection(self) -> List[float]:
        """Convert all items in the collection to floats."""
        return self.map(lambda item: item.get_float())

    def get_bool_collection(self) -> List[bool]:
        """Convert all items in the collection to booleans."""
        return self.map(lambda item: item.get_bool())

    def get_dict_collection(self) -> List[dict]:
        """Convert all items in the collection to dictionaries."""
        return self.map(lambda item: item.get_dict())

    def get_list_collection(self) -> List[AnyList]:
        """Convert all items in the collection to lists."""
        return self.map(lambda item: item.get_list())

    # Non-strict collection conversion methods
    def get_str_or_none_collection(self) -> List[Optional[str]]:
        """Convert all items in the collection to strings or None."""
        return self.map(lambda item: item.get_str_or_none())

    def get_int_or_none_collection(self) -> List[Optional[int]]:
        """Convert all items in the collection to integers or None."""
        return self.map(lambda item: item.get_int_or_none())

    def get_float_or_none_collection(self) -> List[Optional[float]]:
        """Convert all items in the collection to floats or None."""
        return self.map(lambda item: item.get_float_or_none())

    def get_bool_or_none_collection(self) -> List[Optional[bool]]:
        """Convert all items in the collection to booleans or None."""
        return self.map(lambda item: item.get_bool_or_none())

    def get_dict_or_none_collection(self) -> List[Optional[dict]]:
        """Convert all items in the collection to dictionaries or None."""
        return self.map(lambda item: item.get_dict_or_none())

    def get_list_or_none_collection(self) -> List[Optional[AnyList]]:
        """Convert all items in the collection to lists or None."""
        return self.map(lambda item: item.get_list_or_none())

    # Compatibility methods for to_* methods
    def to_str_collection(self) -> List[str]:
        """Convert all items in the collection to strings using to_str()."""
        return self.map(lambda item: item.to_str())

    def to_int_collection(self) -> List[int]:
        """Convert all items in the collection to integers using to_int()."""
        return self.map(lambda item: item.to_int())

    def to_float_collection(self) -> List[float]:
        """Convert all items in the collection to floats using to_float()."""
        return self.map(lambda item: item.to_float())

    def to_bool_collection(self) -> List[bool]:
        """Convert all items in the collection to booleans using to_bool()."""
        return self.map(lambda item: item.to_bool())

    def to_dict_collection(self) -> List[dict]:
        """Convert all items in the collection to dictionaries using to_dict()."""
        return self.map(lambda item: item.to_dict())

    def to_list_collection(self) -> List[AnyList]:
        """Convert all items in the collection to lists using to_list()."""
        return self.map(lambda item: item.to_list())

    # Factory methods
    @classmethod
    def from_config_values(cls, values: List[ConfigValue]) -> 'ConfigValueCollection':
        """Create a ConfigValueCollection from a list of ConfigValue objects."""
        collection = cls()
        collection.extend(values)
        return collection

    @classmethod
    def from_raw_values(cls, values: List[Any]) -> 'ConfigValueCollection':
        """Create a ConfigValueCollection from a list of raw values."""
        return cls.from_config_values([ConfigValue(raw=value) for value in values])
