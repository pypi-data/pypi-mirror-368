from datetime import datetime
from typing import Optional

from codius.domain.model.session.session import Session


def create_session(name: Optional[str] = None) -> Session:
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    session_id = f"{name}_{timestamp}" if name else f"session_{timestamp}"
    return Session(id=session_id)
