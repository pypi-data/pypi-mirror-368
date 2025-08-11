from dataclasses import dataclass
from typing import Dict

from codius.domain.model.plan.plan_examples import PlanExamples


@dataclass(frozen=True)
class PlanChangesPrompt:
    intents: list
    sources: Dict[str, str]
    project_metadata: dict

    def as_prompt(self) -> str:
        import json

        root_prefix = self.project_metadata.get("root_namespace", "").strip()
        example_steps = PlanExamples.all(root_prefix)

        example_blocks = "\n".join(
            f"### {step.description}\n```json\n{json.dumps(step.to_dict(), indent=2)}\n```"
            for step in example_steps
        )

        supported_templates = [
            "domain/model/aggregate/aggregate_root",
            "domain/model/value_object/value_object",
        ]

        template_section = "\n".join(f"- {t}" for t in supported_templates)

        sources_section = "\n\n".join(
            f"### File: {path}\n```csharp\n{content.strip()}\n```"
            for path, content in self.sources.items()
        )

        placement_section = """
        Some modifications (such as `add_method` or `add_property`) require a `"placement"` to specify **where** in the file the change should occur. Supported placement types are:

        - `top_of_class`: Insert at the top of the class, before any members.
        - `bottom_of_class`: Insert at the end of the class.
        - `after_method`: Insert after a method with the given name (use `"reference"`).
        - `before_method`: Insert before a method with the given name.
        - `after_property`: Insert after a property with the given name.
        - `before_property`: Insert before a property with the given name.

        The `"reference"` field in the placement object should refer to an existing method or property name.
        """

        project_context = f"""
Domain path: {self.project_metadata.get('domain_path')}
Application path: {self.project_metadata.get('application_path')}
Infrastructure path: {self.project_metadata.get('infrastructure_path')}
Root namespace: {self.project_metadata.get('root_namespace')}
Persistence provider: {self.project_metadata.get('persistence_provider')}
Database provider: {self.project_metadata.get('database_provider')}
"""

        intents_json = json.dumps(self.intents, indent=2)

        return f"""
You are a Domain-Driven Design (DDD) planning assistant for OpenDDD.NET.

Your task is to plan the necessary code changes for the following modeling intents based on the current project metadata and source files.

For each intent:

- Determine if a new file must be created or an existing file modified.
- Describe each code change as a **plan step** using a JSON object with:
  - `"type"`: `"create_file"` or `"modify_file"`.
  - `"path"`: relative path where the file is created or modified.
  - `"description"`: a short explanation of the change.
  - For `"create_file"`:
    - `"template"`: the name of the template used. Must match one of the supported templates listed below.
    - `"context"`: all required data for the template.
  - For `"modify_file"`:
    - `"modification"`: the kind of modification (`add_method`, `add_property`, etc.).
      - Valid values are:
        - `"add_method"` – Add a method to a class.
        - `"add_property"` – Add a new property to a class.
        - `"remove_method"` – Remove an existing method.
        - `"remove_property"` – Remove an existing property.
        - `"rename_property"` – Rename a property.
    - `"context"`: details about what to add or change.

✅ All C# class, method, and property names must use PascalCase.  
✅ Only return a **JSON list of plan steps** — no markdown, no explanations, no comments.

---

## Supported Templates:

{template_section}

---

## Project Metadata:
{project_context}

---

## Modeling Intents:

```json
{intents_json}
```

---

## Source Files:

{sources_section}

---

## Placement Options

{placement_section.strip()}

---

## Example Plan Steps:

{example_blocks}
"""
