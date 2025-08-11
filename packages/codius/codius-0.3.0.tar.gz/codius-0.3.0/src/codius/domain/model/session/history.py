from dataclasses import dataclass, field
import datetime
from typing import Optional

from codius.domain.model.session.message import Message


@dataclass
class History:
    messages: list[Message] = field(default_factory=list)

    def append(self, role: str, content: str):
        self.messages.append(
            Message(role=role, content=content, timestamp=datetime.datetime.utcnow().isoformat())
        )

    def latest(self) -> Optional[Message]:
        return self.messages[-1] if self.messages else None

    def recent(self, n=4) -> list[Message]:
        return self.messages[-n:]

    def clear(self):
        self.messages.clear()
