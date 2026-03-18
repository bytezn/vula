"""Knowledge base loader for Pfula — loads all SA government services data."""

import json
import os
from pathlib import Path


KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge_base"

# Pre-load all KB files at startup to avoid repeated disk I/O
# NOTE: _load_cache() is called at the BOTTOM of the file, after _format_knowledge is defined.
_KB_CACHE: dict[str, str] = {}

def _load_cache():
    for json_file in sorted(KNOWLEDGE_DIR.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        _KB_CACHE[json_file.stem] = _format_knowledge(data)


def load_all_knowledge() -> str:
    """Load all knowledge base JSON files into a single context string.
    NOTE: ~53k tokens — only use this for bulk/offline contexts.
    Prefer load_knowledge_for_service() for per-request injection.
    """
    return "\n\n---\n\n".join(_KB_CACHE.values())


# Map _detect_service() return values to KB file stems
_SERVICE_TO_KB = {
    "sassa":        "sassa",
    "home_affairs": "home_affairs",
    "uif":          "uif",
    "sars":         "sars",
    "municipal":    "municipal",
    "deeds_office": "deeds_office",
    "cipc":         "cipc",
}


def load_knowledge_for_service(service: str) -> str:
    """Return ONLY the KB section relevant to the detected service (~7-10k tokens).
    Falls back to a compact cross-service cheat-sheet if service is 'general'.
    This keeps per-request input tokens well under 30k rate limit.
    """
    kb_key = _SERVICE_TO_KB.get(service)
    if kb_key and kb_key in _KB_CACHE:
        return f"## {kb_key.replace('_',' ').upper()} KNOWLEDGE\n\n{_KB_CACHE[kb_key]}"

    # General query — return a brief cheat-sheet of contacts/numbers only
    return """## QUICK REFERENCE — KEY CONTACTS
SASSA (grants, SRD): 0800 60 10 11 | sassa.gov.za
Home Affairs (ID, passport, birth cert): 0800 60 11 90 | dha.gov.za
SARS (tax, eFiling): 0800 00 7277 | sars.gov.za
UIF (unemployment, maternity): 0800 843 843 | ufiling.labour.gov.za
eThekwini Municipality: 080 131 3013 | ethekwini.gov.za
CIPC (company registration): 086 100 2472 | cipc.co.za
Deeds Office: 012 338 7200 | deedsoffice.gov.za
Public Protector: 0800 11 20 40
Emergency: 10111 (police) | 10177 (ambulance)"""


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


# Must be called after _format_knowledge is defined above
_load_cache()
