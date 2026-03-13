"""Knowledge base loader for Pfula — loads all SA government services data."""

import json
import os
from pathlib import Path


KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge_base"


def load_all_knowledge() -> str:
    """Load all knowledge base JSON files into a single context string."""
    knowledge_parts = []

    for json_file in sorted(KNOWLEDGE_DIR.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        knowledge_parts.append(_format_knowledge(data))

    return "\n\n---\n\n".join(knowledge_parts)


def _format_knowledge(data: dict, indent: int = 0) -> str:
    """Recursively format a knowledge base dict into readable text."""
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        readable_key = key.replace("_", " ").title()

        if isinstance(value, str):
            lines.append(f"{prefix}{readable_key}: {value}")
        elif isinstance(value, list):
            lines.append(f"{prefix}{readable_key}:")
            for item in value:
                if isinstance(item, str):
                    lines.append(f"{prefix}  - {item}")
                elif isinstance(item, dict):
                    lines.append(_format_knowledge(item, indent + 1))
                    lines.append("")
        elif isinstance(value, dict):
            lines.append(f"{prefix}{readable_key}:")
            lines.append(_format_knowledge(value, indent + 1))
        else:
            lines.append(f"{prefix}{readable_key}: {value}")

    return "\n".join(lines)


def get_knowledge_summary() -> dict:
    """Return a summary of available knowledge base files."""
    summary = {}
    for json_file in sorted(KNOWLEDGE_DIR.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        summary[json_file.stem] = data.get("service", json_file.stem)
    return summary
