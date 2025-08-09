from enum import Enum
from typing import Any


def get_git_name(val: Any) -> str | None:
    """Get the appropriate gittable name for a value, handling various types."""
    if isinstance(val, Enum):
        return val.name
    if isinstance(val, float):
        return str(round(val, 3))
    if val is not None:
        return str(val)
    return None
