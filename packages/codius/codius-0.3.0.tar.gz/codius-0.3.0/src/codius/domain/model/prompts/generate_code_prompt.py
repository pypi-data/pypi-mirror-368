from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class GenerateCodePrompt:
    plan: dict
    building_blocks: List[dict]
    example: str = ""

    def as_prompt(self) -> str:
        blocks_summary = "\n".join(
            f"- {bb.get('type')}: {bb.get('name')} ({bb.get('namespace')})"
            for bb in self.building_blocks
        ) or "[No existing building blocks found]"

        example_section = (
            f"\n\n### Example of a {self.plan.get('template')}:\n\n```csharp\n{self.example}\n```"
            if self.example else ""
        )

        return f"""
You are a senior .NET developer using the OpenDDD.NET framework to implement Domain-Driven Design (DDD) patterns.

Here is the current list of existing building blocks:
{blocks_summary}

Here is the planned change to implement (structured as a JSON object):
{self.plan}

Your task is to generate the required code files to fulfill this plan.

- Follow C# 12 and .NET 8 syntax
- Use OpenDDD.NET conventions (aggregate roots, actions, domain services, events, adapters, etc.)
- If the plan specifies a namespace, use it. Otherwise, follow standard conventions.
- Only include meaningful domain logic (don't overcomment or add generic boilerplate)

{example_section}

Now generate the code. Return only a single valid JSON object like this:

{{
  "files": [
    {{
      "path": "Domain/Order/ProductBundle.cs",
      "content": "<full file content>"
    }},
    ...
  ]
}}
"""
