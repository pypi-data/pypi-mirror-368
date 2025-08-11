from dataclasses import dataclass
import json
from codius.domain.model.prompts.distill_intent_prompt import DistillIntentPrompt


@dataclass(frozen=True)
class ReviseIntentPrompt:
    summary: str
    user_input: str
    revision_history: list
    current_plan: list
    current_feedback: str

    def as_prompt(self) -> str:
        history_blocks = ""
        for i, rev in enumerate(self.revision_history):
            history_blocks += f"""

### Revision {i + 1}

The assistant previously proposed this intent and plan:

```json
{json.dumps(rev['intent'], indent=2)}
```

```json
{json.dumps(rev['plan'], indent=2)}
```

The user responded:

\"{rev['feedback']}\"
"""

        current_block = f"""
### Current Plan

The assistant now proposed:

```json
{json.dumps(self.current_plan, indent=2)}
```

The user wants to revise it with the following feedback:

\"{self.current_feedback}\"
"""

        composed_input = f"""You are a modeling assistant for a Domain-Driven Design (DDD) codebase built with OpenDDD.NET.

The user originally asked:

\"{self.user_input.strip()}\"

{history_blocks}
{current_block}

Please revise the modeling intent accordingly and return it as a valid JSON array of intents.
"""

        return DistillIntentPrompt(summary=self.summary, user_input=composed_input).as_prompt()
