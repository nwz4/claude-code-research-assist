#!/usr/bin/env python3
"""
Minimal research-assist backend template.

This is a template only. Fill in your own API calls for Exa, Tavily,
optional Grok bridge, and any evidence normalization you need.
The Claude Code skill does not require this script to exist, but this file
documents one clean integration point for a unified research-assist backend.
"""

import json
import os
import sys


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def main() -> int:
    payload = {
        "query": sys.argv[1] if len(sys.argv) > 1 else "",
        "exa_configured": bool(env("EXA_API_KEY")),
        "tavily_configured": bool(env("TAVILY_API_KEY")),
        "grok_bridge_configured": bool(env("GROK_BRIDGE_BASE_URL")),
        "notes": [
            "Implement Exa/Tavily/Grok calls here if you want a unified local backend.",
            "Prefer an evidence-first schema with title/url/source/snippet fields.",
            "Keep DOI/arXiv/title-based dedupe in the backend or a later processing step.",
            "Do not make this script a hard dependency of the skill.",
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
