"""Boolean database type."""

from typing import Any, Union

from mocksmith.types.base import DBType


class BOOLEAN(DBType[bool]):
    """Boolean type."""

    @property
    def sql_type(self) -> str:
        return "BOOLEAN"

    @property
    def python_type(self) -> type[bool]:
        return bool

    def _validate_custom(self, value: Any) -> None:
        """Validate boolean value."""
        # Accept various truthy/falsy representations
        valid_types = (bool, int, str)
        if not isinstance(value, valid_types):
            raise ValueError(f"Expected boolean-like value, got {type(value).__name__}")

        if isinstance(value, str):
            if value.lower() not in ("true", "false", "1", "0", "t", "f", "yes", "no", "y", "n"):
                raise ValueError(f"Invalid boolean string: {value}")

    def _serialize(self, value: Union[bool, int, str]) -> bool:
        if isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return bool(value)
        else:  # str
            return value.lower() in ("true", "1", "t", "yes", "y")

    def _deserialize(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return bool(value)
        elif isinstance(value, str):
            return value.lower() in ("true", "1", "t", "yes", "y")
        else:
            return bool(value)
