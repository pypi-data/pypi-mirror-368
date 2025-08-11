import logging

from codius.infrastructure.services.llm_service import LlmService
from codius.domain.model.prompts.plan_changes_prompt import PlanChangesPrompt

logger = logging.getLogger(__name__)


def plan_changes(state: dict) -> dict:
    from codius.di import container

    logger.debug("Running plan_all_with_llm with state keys: %s", list(state.keys()))

    try:
        prompt = PlanChangesPrompt(
            intents=state["intent"],
            sources=state["sources"],
            project_metadata=state["project_metadata"]
        ).as_prompt()

        logger.debug("Constructed plan_all_with_llm prompt (%d chars)", len(prompt))

        llm_service = container.resolve(LlmService)

        logger.debug("Calling LLM to generate plan...")
        response = llm_service.call_prompt(prompt)
        logger.debug("LLM response received.")
    except Exception as e:
        logger.error("Error during plan_all_with_llm: %s", e)
        state["plan"] = [{"operation": "error", "error_message": str(e)}]
        return state

    state["plan"] = llm_service.try_extract_json(response)
    return state
