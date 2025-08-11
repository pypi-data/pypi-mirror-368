from dataclasses import dataclass
from typing import List, Optional

from codius.domain.model.intents.location import Location
from codius.domain.model.intents.method_implementation import MethodImplementation
from codius.domain.model.intents.parameter import Parameter


@dataclass
class Method:
    name: str
    parameters: Optional[List[Parameter]] = None
    return_type: Optional[str] = None
    is_async: Optional[bool] = True
    location: Optional[Location] = None
    implementation: Optional[MethodImplementation] = None
