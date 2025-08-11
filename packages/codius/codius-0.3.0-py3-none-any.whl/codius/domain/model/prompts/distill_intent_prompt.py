from dataclasses import dataclass
from codius.domain.model.intents.intent_type import IntentType
from codius.domain.model.intents.database_provider import DatabaseProvider
from codius.domain.model.intents.persistence_provider import PersistenceProvider

from codius.domain.model.intents.aggregate.add_aggregate_intent import AddAggregateIntent
from codius.domain.model.intents.aggregate.remove_aggregate_intent import RemoveAggregateIntent
from codius.domain.model.intents.aggregate.add_aggregate_method_intent import AddAggregateMethodIntent
from codius.domain.model.intents.aggregate.remove_aggregate_method_intent import RemoveAggregateMethodIntent
from codius.domain.model.intents.aggregate.add_aggregate_property_intent import AddAggregatePropertyIntent
from codius.domain.model.intents.aggregate.remove_aggregate_property_intent import RemoveAggregatePropertyIntent
from codius.domain.model.intents.aggregate.add_aggregate_method_parameter_intent import AddAggregateMethodParameterIntent
from codius.domain.model.intents.aggregate.remove_aggregate_method_parameter_intent import RemoveAggregateMethodParameterIntent
from codius.domain.model.intents.repository.add_repository_method_intent import \
    AddRepositoryMethodIntent
from codius.domain.model.intents.repository.remove_repository_intent import \
    RemoveRepositoryIntent
from codius.domain.model.intents.repository.remove_repository_method_intent import \
    RemoveRepositoryMethodIntent
from codius.domain.model.intents.value_object.add_value_object_intent import AddValueObjectIntent
from codius.domain.model.intents.value_object.remove_value_object_intent import RemoveValueObjectIntent
from codius.domain.model.intents.value_object.add_value_object_property_intent import AddValueObjectPropertyIntent
from codius.domain.model.intents.value_object.remove_value_object_property_intent import RemoveValueObjectPropertyIntent
from codius.domain.model.intents.repository.add_repository_intent import AddRepositoryIntent
from codius.infrastructure.services.code_scanner.model.building_block_type import \
    BuildingBlockType


@dataclass(frozen=True)
class DistillIntentPrompt:
    summary: str
    user_input: str

    def as_prompt(self) -> str:
        example_intents = [
            AddAggregateIntent,
            AddAggregateMethodIntent,
            AddAggregatePropertyIntent,
            AddAggregateMethodParameterIntent,
            RemoveAggregateIntent,
            RemoveAggregateMethodIntent,
            RemoveAggregatePropertyIntent,
            RemoveAggregateMethodParameterIntent,
            AddValueObjectIntent,
            AddValueObjectPropertyIntent,
            RemoveValueObjectIntent,
            RemoveValueObjectPropertyIntent,
            AddRepositoryIntent,
            AddRepositoryMethodIntent,
            RemoveRepositoryIntent,
            RemoveRepositoryMethodIntent,
        ]

        all_blocks = {bb.value for bb in BuildingBlockType}
        supported_blocks = {intent.building_block.value for intent in IntentType if
                            intent != IntentType.UNSURE}
        unsupported_blocks = all_blocks - supported_blocks

        supported_blocks_text = "\n".join(f"- {b}" for b in sorted(supported_blocks))
        unsupported_blocks_text = "\n".join(f"- {b}" for b in sorted(unsupported_blocks))

        example_blocks = "\n".join(
            f"### {cls.intent.value}\n```json\n{cls.to_example_json()}\n```"
            for cls in example_intents
        )

        supported_intents_text = "\n".join(f"- {intent.value}" for intent in IntentType if intent != IntentType.UNSURE)
        persistence_text = "\n".join(f"- {p.value}" for p in PersistenceProvider)
        database_text = "\n".join(f"- {d.value}" for d in DatabaseProvider)

        context_section = f"""
### Context

Previous modeling session summary:

{self.summary.strip()}
""" if self.summary else ""

        return f"""
You are a modeling assistant for a Domain-Driven Design (DDD) codebase built with OpenDDD.NET.

{context_section}
The user has written the following instruction:

"{self.user_input}"

Your task is to extract the modeling **intents** from this instruction and return them as a **list of valid JSON objects**, one per granular intent.

You may only choose from the following supported intents:

{supported_intents_text}

For `"add_repository"` intents, the supported values are:

**Persistence Providers**:
{persistence_text}

**Database Providers**:
{database_text}

---

### Known DDD Building Blocks

These are the known building blocks in Domain-Driven Design:

**Supported:**
{supported_blocks_text}

**Not yet supported:**
{unsupported_blocks_text}

If the user refers to a known DDD building block that is **not yet supported**, return:

```json
{{ "intent": "unsupported", "building_block": "<block_name>" }}
```

If the user's intent is unclear or unsupported, respond only with:

```json
{{ "intent": "unsure" }}

### Instructions

- Break complex modeling instructions into small, **granular intents**.
- Return **one JSON object per distinct modeling action**.
- Do not combine multiple operations into one intent (e.g. don’t add methods and properties in the same intent).
- Only include methods, properties, or parameters if the user explicitly describes them.
- If the user describes a method, the implementation should be generated unless the user says something else.
- Use empty arrays/lists for optional fields if the user didn’t specify them.
- If the user simply asks to create a building block without details, generate a minimal scaffold.
- Return valid JSON only. No comments, markdown, or extra explanations.
- Avoid comments or docstrings unless necessary to clarify complex logic in rare cases.
- Extract one intent per operation. If the user describes multiple operations (e.g., adding two aggregates and a method), return a list of multiple intent JSON objects.
- Always return a **list** of intent objects, even if there's only one.

### Output Format

Return a JSON array where each element is an intent object.

### Examples:

{example_blocks}
"""
