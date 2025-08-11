import logging

logger = logging.getLogger(__name__)


def route_by_intent(state: dict) -> str:
    intents = state.get("intent", [])
    logger.debug("Routing by intent. Intents: %s", intents)

    if isinstance(intents, list):
        for intent in intents:
            if not isinstance(intent, dict):
                continue
            intent_type = intent.get("intent", "").strip().lower()
            logger.debug("Intent type found: %s", intent_type)

            if intent_type == "error":
                return "error"
            elif intent_type == "unsupported":
                return "unsupported"
            elif intent_type and intent_type not in {"none", "greeting", "unsure"}:
                return "valid"

    logger.debug("No valid intent found, routing to 'unclear'")
    return "unclear"
