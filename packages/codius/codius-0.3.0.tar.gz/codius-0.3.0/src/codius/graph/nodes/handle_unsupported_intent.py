from typing import cast


def handle_unsupported_intent(state: dict) -> dict:
    from codius.domain.model.intents.intent_type import IntentType

    unsupported_blocks = {
        intent.get("building_block")
        for intent in state.get("intent", [])
        if intent.get("intent") == "unsupported"
    }
    block_list = ", ".join(sorted(unsupported_blocks))

    # Dynamically get supported building blocks
    supported_blocks = {
        intent.building_block.value
        for intent in IntentType
        if intent != IntentType.UNSURE
    }
    supported_blocks_list = "\n".join(f"- {b}" for b in sorted(supported_blocks))

    state["final_output"] = (
        f"⚠️ The assistant understood your request, but the following building block(s) aren't supported yet:\n"
        f"- {block_list}\n\n"
        "We're shipping updates frequently, so it might already be available in a newer version.\n\n"
        "👉 Try updating Codius:\n"
        "```bash\npip install --upgrade codius\n```\n"
        "Then rerun your request.\n\n"
        "In the meantime, you can try working with one of the currently supported building blocks:\n"
        f"{supported_blocks_list}\n\n"
        "💡 Need help or want to request this feature? Let us know on GitHub!"
    )

    return state
