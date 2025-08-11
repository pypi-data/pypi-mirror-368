import logging

from codius.domain.model.prompts.distill_intent_prompt import DistillIntentPrompt
from codius.infrastructure.services.llm_service import LlmService

logger = logging.getLogger(__name__)


def distill_intent(state: dict) -> dict:
    from codius.di import container

    logger.debug("Running distill_intent with state keys: %s", list(state.keys()))

    try:
        prompt = DistillIntentPrompt(summary=state["summary"],
                                     user_input=state["user_input"]).as_prompt()
        logger.debug("Constructed distill intent prompt (%d chars)", len(prompt))

        llm_service = container.resolve(LlmService)

        logger.debug("Calling LLM to distill intent...")
        response = llm_service.call_prompt(prompt)
        logger.debug("LLM response received.")
    except Exception as e:
        logger.error("Error during intent distillation: %s", e)
        state["intent"] = {"intent": "error", "error_message": str(e)}
        return state

    parsed = llm_service.try_extract_json(response)

    intents = []
    if isinstance(parsed, list):
        logger.debug("Multiple intents detected (%d)", len(parsed))
        intents = parsed
    elif isinstance(parsed, dict):
        logger.debug("Extracted intent: %s", parsed.get("intent"))
        intents = [parsed]
    else:
        logger.warning("Unexpected intent format: %s", type(parsed))

    state["intent"] = intents  # No post-processing
    return state
