def route_by_user_approval(state: dict) -> str:
    approval = state.get("approval", "").lower()

    if approval in {"yes", "apply", "y"}:
        return "apply"

    if approval in {"revise", "change"}:
        return "revise"

    return "abort"
