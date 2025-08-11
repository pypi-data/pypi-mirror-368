import logging

from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def extract_relevant_sources(state: dict) -> dict:
    intents = state.get("intent", [])
    building_blocks = state.get("building_blocks", [])
    sources: Dict[str, str] = {}

    # Index building blocks by (type, name)
    blocks_by_key = {
        (bb["type"], bb["name"]): bb
        for bb in building_blocks
    }

    # Derive paths from intents
    seen_paths = set()

    for intent in intents:
        key = (intent.get("building_block_type"), intent.get("target"))
        block = blocks_by_key.get(key)
        if block:
            path = Path(block["file_path"])
            if path not in seen_paths:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        sources[str(path)] = f.read()
                        seen_paths.add(path)
                except FileNotFoundError:
                    logger.warning(f"⚠️ Source file not found: {path}")
                except Exception as e:
                    logger.error(f"❌ Failed to read file {path}: {e}")

    logger.info(f"✅ Extracted {len(sources)} source file(s).")
    state["sources"] = sources
    return state
