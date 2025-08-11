import logging
import re

logger = logging.getLogger(__name__)


def enrich_intents(state: dict) -> dict:
    logger.debug("Running enrich_intents...")

    intents = state.get("validated_intents", [])

    # Build lookups for aggregate and repository intents
    aggregates_by_target = {
        i["target"]: i for i in intents if i.get("intent") == "add_aggregate"
    }
    repositories_by_target = {
        i["target"]: i for i in intents if i.get("intent") == "add_repository"
    }

    enriched_intents = intents.copy()

    for target, repo_intent in repositories_by_target.items():
        aggregate_intent = aggregates_by_target.get(target)
        if aggregate_intent:
            enriched_agg = _inject_missing_properties_from_repo_methods(aggregate_intent, repo_intent)
            if enriched_agg is not aggregate_intent:
                # Replace old aggregate with enriched one
                enriched_intents = [
                    enriched_agg if i is aggregate_intent else i
                    for i in enriched_intents
                ]

    state["enriched_intents"] = enriched_intents
    logger.debug("Enriched %d intent(s)", len(enriched_intents))
    return state


def _inject_missing_properties_from_repo_methods(aggregate_intent: dict, repository_intent: dict) -> dict:
    """Infer and inject missing aggregate properties based on repository method patterns."""
    agg_details = aggregate_intent.setdefault("details", {})
    properties = agg_details.setdefault("properties", [])
    existing_props = {p["name"] for p in properties}
    added_props = []

    for method in repository_intent.get("details", {}).get("custom_methods", []):
        method_name = method.get("name", "")
        if not method_name.endswith("Async"):
            continue

        base = method_name[:-5]  # remove 'Async'

        if base.startswith(("GetBy", "FindBy", "FindWith")):
            suffix = base.replace("GetBy", "").replace("FindBy", "").replace("FindWith", "")
            if suffix:
                prop_name = _to_pascal_case(suffix)
                if prop_name not in existing_props:
                    param = _find_param_by_pascal_name(method.get("parameters", []), prop_name)
                    prop_type = param.get("type", "string") if param else "string"

                    new_prop = {"name": prop_name, "type": prop_type}
                    properties.append(new_prop)
                    added_props.append(prop_name)

    if added_props:
        logger.info(
            "Inferred %d new property(ies) for aggregate '%s': %s",
            len(added_props), aggregate_intent.get("target"), added_props
        )

    return aggregate_intent


def _find_param_by_pascal_name(parameters, pascal_name: str):
    for p in parameters:
        if _to_pascal_case(p.get("name", "")) == pascal_name:
            return p
    return None


def _to_pascal_case(name: str) -> str:
    if not name:
        return name
    words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?![a-z])', name)
    return ''.join(w.capitalize() for w in words)
