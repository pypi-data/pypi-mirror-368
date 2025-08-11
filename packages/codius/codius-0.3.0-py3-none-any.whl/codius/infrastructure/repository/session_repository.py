import json

from datetime import datetime
from pathlib import Path

from codius.domain.model.session.session import Session
from codius.domain.model.session.state import State
from codius.domain.model.session.history import History, Message
from codius.infrastructure.repository.base_repository import BaseRepository
from codius.infrastructure.services.project_metadata_service import ProjectMetadataService


class SessionRepository(BaseRepository[Session]):
    def __init__(self, metadata_service: ProjectMetadataService):
        self.metadata_service = metadata_service

    def get(self, id: str) -> Session:
        session_path = self._get_session_path(id)
        state_path = session_path / "state.json"
        history_path = session_path / "history.json"

        # Load state
        if state_path.exists():
            state_data = json.loads(state_path.read_text())
            state = State.from_dict(state_data)
        else:
            state = State()

        # Load history
        if history_path.exists():
            history_data = json.loads(history_path.read_text())
            messages = [Message(**m) for m in history_data]
            history = History(messages)
        else:
            history = History()

        created_at = self._id_to_iso8601(id)

        return Session(id=id, state=state, history=history, created_at=created_at)

    def get_all(self) -> list[Session]:
        sessions_path = self.metadata_service.get_sessions_path()
        if not sessions_path.exists():
            return []

        return [
            self.get(p.name)
            for p in sessions_path.iterdir()
            if p.is_dir() and p.name != "active"
        ]

    def save(self, session: Session) -> None:
        session_path = self._get_session_path(session.id)
        session_path.mkdir(parents=True, exist_ok=True)
        (session_path / "generated").mkdir(exist_ok=True)

        # Save state
        state_path = session_path / "state.json"
        state_path.write_text(json.dumps(session.state.to_dict(), indent=2))

        # Save history
        history_path = session_path / "history.json"
        messages = [m.__dict__ for m in session.history.messages]
        history_path.write_text(json.dumps(messages, indent=2))

        # Update active session pointer
        active_file = self._get_active_file_path()
        active_file.write_text(session.id)

    def delete(self, id: str) -> None:
        path = self._get_session_path(id)
        if path.exists():
            for file in path.glob("*"):
                file.unlink()
            path.rmdir()

    def get_active_session(self) -> Session:
        active_file = self._get_active_file_path()
        session_id = active_file.read_text().strip()
        return self.get(session_id)

    def _get_session_path(self, session_id: str) -> Path:
        return self.metadata_service.get_sessions_path() / session_id

    def _get_active_file_path(self) -> Path:
        return self.metadata_service.get_sessions_path() / "active"

    def _id_to_iso8601(self, id: str) -> str:
        try:
            ts_part = id.replace("session_", "")
            dt = datetime.strptime(ts_part, "%Y-%m-%dT%H-%M-%S")
            return dt.isoformat(timespec="seconds")
        except ValueError:
            raise ValueError(f"Invalid id format: {id}")
