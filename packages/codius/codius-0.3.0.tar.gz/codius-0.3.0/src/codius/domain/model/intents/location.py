from dataclasses import dataclass
from typing import Literal


@dataclass
class Location:
    position: Literal["before", "after"]
    reference: str  # e.g., the name of the method or property
