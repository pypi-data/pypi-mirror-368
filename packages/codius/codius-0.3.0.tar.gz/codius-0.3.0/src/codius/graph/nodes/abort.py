def abort(state: dict) -> dict:
    state["final_output"] = "❌ Changes aborted by user."
    return state
