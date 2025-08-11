from dataclasses import dataclass, field
from datetime import datetime, timedelta

from codius.domain.model.session.history import History
from codius.domain.model.session.state import State

SESSION_EXPIRY_HOURS = 6


@dataclass
class Session:
    id: str
    state: State = field(default_factory=State)
    history: History = field(default_factory=History)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def update_with_graph_result(self, result: dict):
        self.append_user_message(result["user_input"])
        self.state.update_with_graph_result(result)

    def append_user_message(self, content: str):
        self.history.append("user", content)

    def append_assistant_message(self, content: str):
        self.history.append("assistant", content)

    def clear_state(self):
        """Resets both state and history."""
        self.state = State()

    def clear_state_for_repl_cycle(self):
        self.state.clear_for_repl_cycle()

    def clear(self):
        """Resets both state and history."""
        self.state = State()
        self.history.clear()

    def clear_history(self):
        """Clears only history."""
        self.history.clear()

    def apply_compaction(self, summary: str):
        self.state.summarize(summary)
        self.history.clear()

    def should_be_replaced(self) -> bool:
        try:
            created = datetime.fromisoformat(self.created_at)
            is_old = datetime.utcnow() - created > timedelta(hours=SESSION_EXPIRY_HOURS)
        except Exception:
            is_old = False

        compacted = bool(self.state.summary)
        has_new_messages = len(self.history.messages) > 0

        return (compacted and not has_new_messages) or is_old
