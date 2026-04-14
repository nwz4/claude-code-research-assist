# research-assist

Unified Claude Code skill for paper discovery, research thinking, method comparison, claim verification, and Playwright-assisted academic source collection.

中文首页：[`README.md`](./README.md)

## What it does

`research-assist` is a single core skill for research workflows. It covers four common use cases with one reusable foundation:

- **paper-search**: discover papers, surveys, benchmarks, project pages, and code
- **research-think**: brainstorm ideas, identify open questions, and propose next queries
- **paper-compare**: compare methods, assumptions, datasets, metrics, and conclusions
- **claim-verify**: verify whether a claim is supported, partially supported, or still unverified

It uses a **dual-lane workflow**:

### 1. Search evidence lane
- discover sources through Exa / Tavily / WebSearch
- collect URL-first evidence
- deduplicate and prioritize sources

### 2. Grok synthesis lane
- run query expansion
- produce claims / disagreements / next_queries
- support comparison and hypothesis generation

When public pages are insufficient, the workflow can also produce **Playwright fallback** hints for restricted academic sites such as IEEE, ACM, Springer, and ScienceDirect.

## What you must configure yourself

This repository does **not** ship with usable API credentials, browser login state, or remote bridge services. To enable the enhanced workflow, you must configure the following items yourself:

### Required for local aggregation
- `EXA_API_KEY`
- `TAVILY_API_KEY`

### Required for Grok-powered synthesis
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL` (recommended: `auto`)

### Required for restricted-site fallback
- a local Playwright-capable browser environment
- your own login session for IEEE / ACM / Springer / ScienceDirect when needed

### Optional but recommended
- Python 3 available as `python3`
- a private local config file copied from `templates/research.env.example`, such as `templates/research.local.env`

## How Grok access works in this project

This project does **not** call a native official Grok API directly.

Instead, Grok access is expected to come from **Grok2API**, used as an OpenAI-compatible bridge layer.

Reference:
- https://github.com/chenyme/grok2api

In practice, that means:
- you run or provide a Grok2API service yourself
- `research-assist` talks to that service through OpenAI-style endpoints
- the backend mainly uses:
  - `GET /v1/models`
  - `POST /v1/chat/completions`

If you do not deploy Grok2API yourself, Grok-related modes will not work.

## Repository layout

```text
research-assist/
├─ LICENSE
├─ SKILL.md
├─ README.md
├─ README.en.md
├─ README.zh-CN.md
├─ .gitignore
├─ scripts/
│  └─ research_aggregate.py
├─ templates/
│  ├─ research.env.example
│  ├─ api-config-template.md
│  └─ search_aggregator_template.py
└─ references/
   ├─ api-setup.md
   ├─ dedup-rules.md
   ├─ grok-bridge.md
   ├─ login-fallback.md
   ├─ research-report-template.md
   └─ source-priority.md
```

## Setup

Copy the example env file and fill in your own local configuration:

```bash
cp "research-assist/templates/research.env.example" "research-assist/templates/research.local.env"
```

Main variables:
- `EXA_API_KEY`
- `TAVILY_API_KEY`
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL=auto`

See:
- `research-assist/references/api-setup.md`
- `research-assist/references/grok-bridge.md`
- `research-assist/templates/api-config-template.md`

## Usage examples

### Check CLI help

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" --help
```

### Aggregate mode

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --query "multimodal retrieval augmented generation survey" \
  --max-results 5
```

### Think mode: idea generation

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-idea \
  --query "efficient multimodal rag for long documents" \
  --max-results 5
```

### Think mode: comparison

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-compare \
  --query "AAA interpolation for electromagnetics" \
  --compare-target "vector fitting" \
  --max-results 5
```

### Think mode: verification

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-verify \
  --query "multimodal RAG reliability" \
  --max-results 5
```

## Output model

The backend uses an evidence-first schema, including fields such as:

- `results`
- `lanes.search_lane.evidence`
- `lanes.search_lane.playwright_hints`
- `lanes.grok_lane.claims`
- `synthesis.validated_claims`
- `synthesis.disagreements`
- `synthesis.next_queries`

## What to publish

Publish:
- `research-assist/README.md`
- `research-assist/README.en.md`
- `research-assist/README.zh-CN.md`
- `research-assist/.gitignore`
- `research-assist/LICENSE`
- `research-assist/SKILL.md`
- `research-assist/scripts/research_aggregate.py`
- `research-assist/templates/research.env.example`
- `research-assist/templates/api-config-template.md`
- `research-assist/templates/search_aggregator_template.py`
- `research-assist/references/api-setup.md`
- `research-assist/references/dedup-rules.md`
- `research-assist/references/grok-bridge.md`
- `research-assist/references/login-fallback.md`
- `research-assist/references/research-report-template.md`
- `research-assist/references/source-priority.md`

Do **not** publish:
- `research-assist/templates/research.local.env`

## Notes

- Grok is used for synthesis, not as a substitute for formal sources.
- Grok access in this repository is expected to come from a **Grok2API** bridge, not direct native Grok API usage.
- Claims should be checked against URL-backed evidence whenever possible.
- Playwright is intended as a targeted fallback for restricted academic sites.
