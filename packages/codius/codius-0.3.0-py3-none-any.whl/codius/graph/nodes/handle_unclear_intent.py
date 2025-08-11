def handle_unclear_intent(state: dict) -> dict:
    state["final_output"] = (
        "👋 Hello! I couldn't quite determine your intent.\n\n"
        "You can ask me to generate an aggregate, action, listener, etc.\n"
        "Try something like:\n\n"
        "- 'Create an Order aggregate with line items'\n"
        "- 'Add an UpdateCustomerNameAction'\n"
        "- 'Generate a domain event for CustomerRegistered'\n"
    )
    return state
