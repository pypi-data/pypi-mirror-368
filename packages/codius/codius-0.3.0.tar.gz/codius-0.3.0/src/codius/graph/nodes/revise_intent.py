import logging

from codius.domain.model.prompts.revise_intent_prompt import ReviseIntentPrompt
from codius.infrastructure.services.llm_service import LlmService

logger = logging.getLogger(__name__)


def revise_intent(state: dict) -> dict:
    from codius.di import container

    logger.debug("Running revise_intent...")

    # Build revision history entry from current state
    revision_entry = {
        "feedback": state.get("revision_feedback", ""),
        "intent": state.get("intent", []),
        "plan": state.get("plan", [])
    }

    # Append to revision history
    state.setdefault("revision_history", []).append(revision_entry)

    # Create and send revised prompt
    prompt = ReviseIntentPrompt(
        summary=state.get("summary", ""),
        user_input=state.get("user_input", ""),
        revision_history=state["revision_history"][:-1],  # all previous rounds
        current_plan=state.get("plan", []),
        current_feedback=state.get("revision_feedback", "")
    ).as_prompt()

    logger.debug("Constructed revise intent prompt (%d chars)", len(prompt))

    llm_service = container.resolve(LlmService)

    try:
        logger.debug("Calling LLM to revise intent...")
        response = llm_service.call_prompt(prompt)
        logger.debug("LLM response received.")
    except Exception as e:
        logger.error("Error during revise intent LLM call: %s", e)
        state["intent"] = [{"intent": "error", "error_message": str(e)}]
        return state

    parsed = llm_service.try_extract_json(response)

    if not parsed:
        logger.warning("LLM response could not be parsed. Marking intent as 'unsure'.")
        state["intent"] = [{"intent": "unsure"}]
    elif isinstance(parsed, dict):
        state["intent"] = [parsed]
    elif isinstance(parsed, list):
        state["intent"] = parsed
    else:
        logger.error("Unexpected format from LLM: %s", type(parsed))
        state["intent"] = [{"intent": "unsure"}]

    state["revise_mode"] = True
    return state
