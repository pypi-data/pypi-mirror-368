def handle_intent_error(state: dict) -> dict:
    error_msg = state.get("intent", [{}])[0].get("error_message", "Unknown error")
    state["final_output"] = f"❌ An error occurred while distilling intent: {error_msg}"
    state["approval"] = "abort"
    return state
