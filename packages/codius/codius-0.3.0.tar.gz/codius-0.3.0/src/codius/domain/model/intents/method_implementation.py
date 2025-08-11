from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class MethodImplementation:
    type: Optional[Literal["generate", "not_implemented", "none"]] = "none"
    hint: Optional[str] = None
