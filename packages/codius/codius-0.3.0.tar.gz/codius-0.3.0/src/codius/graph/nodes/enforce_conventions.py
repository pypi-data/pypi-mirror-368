import logging
import re

logger = logging.getLogger(__name__)


def enforce_conventions(state: dict) -> dict:
    logger.debug("Running enforce_conventions...")

    enforced_intents = []

    for intent in state.get("intent", []):
        intent_type = intent.get("intent")

        if intent_type == "add_aggregate":
            enforced_intents.append(_enforce_aggregate_conventions(intent))
        elif intent_type == "add_repository":
            enforced_intents.append(_enforce_repository_conventions(intent))
        elif intent_type == "remove_aggregate":
            logger.debug("Enforcing remove_aggregate conventions (noop)...")
            enforced_intents.append(intent)
        else:
            logger.warning("No conventions defined for intent type: %s", intent_type)
            enforced_intents.append(intent)

    state["conventional_intents"] = enforced_intents
    logger.debug("Enforced conventions on %d intent(s)", len(enforced_intents))
    return state


def _enforce_aggregate_conventions(intent: dict) -> dict:
    logger.debug("Enforcing aggregate conventions...")

    details = intent.setdefault("details", {})
    properties = details.setdefault("properties", [])

    # Normalize property names to PascalCase
    for prop in properties:
        original_name = prop.get("name", "")
        pascal_name = _to_pascal_case(original_name)
        if original_name != pascal_name:
            logger.debug("Renaming property '%s' -> '%s'", original_name, pascal_name)
            prop["name"] = pascal_name

    # TODO: Enforce command/event naming if needed

    return intent


def _enforce_repository_conventions(intent: dict) -> dict:
    logger.debug("Enforcing repository conventions...")

    details = intent.setdefault("details", {})
    methods = details.get("custom_methods", [])

    for method in methods:
        method.setdefault("is_async", True)

        name = method.get("name")
        if name and not name.endswith("Async"):
            method["name"] = f"{name}Async"

        parameters = method.setdefault("parameters", [])
        for param in parameters:
            original_name = param.get("name", "")
            camel_name = _to_camel_case(original_name)
            if original_name != camel_name:
                logger.debug("Renaming parameter '%s' -> '%s'", original_name, camel_name)
                param["name"] = camel_name

    return intent


def _to_pascal_case(name: str) -> str:
    """Convert string to PascalCase"""
    if not name:
        return name
    words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?![a-z])', name)
    return ''.join(word.capitalize() for word in words)


def _to_camel_case(name: str) -> str:
    """Convert string to camelCase"""
    if not name:
        return name
    pascal = _to_pascal_case(name)
    return pascal[0].lower() + pascal[1:] if len(pascal) > 1 else pascal.lower()
