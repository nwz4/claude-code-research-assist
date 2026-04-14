# research-assist

Unified Claude Code skill for **paper discovery, research thinking, method comparison, and claim verification**.

Chinese homepage: [`README.md`](./README.md)

## At a glance

`research-assist` is not just a paper search tool. It is an **evidence-first research workflow** built around four common use cases:

| Mode | What it helps with | Typical output |
| --- | --- | --- |
| `paper-search` | find papers, surveys, benchmarks, project pages, code | reading list, source links, supporting resources |
| `research-think` | brainstorm ideas, decompose directions, plan next searches | candidate ideas, open problems, next queries |
| `paper-compare` | compare methods, assumptions, datasets, metrics, conclusions | differences, trade-offs, disagreement points |
| `claim-verify` | verify whether a claim holds | supported / partial / unverified |

## Why this skill is useful

- **One entry point** for search, comparison, ideation, and verification
- **Evidence first**: conclusions should carry URLs whenever possible
- **Dual-lane design**: search lane gathers evidence, Grok lane synthesizes and fills gaps
- **Restricted sites are still workable**: Playwright fallback can help with IEEE / ACM / Springer / ScienceDirect

## How it works

### 1. Search evidence lane
- discover sources with Exa / Tavily / WebSearch
- organize findings around URLs
- deduplicate, aggregate, and prioritize sources

### 2. Grok synthesis lane
- run query expansion
- produce claims / disagreements / next_queries
- support comparison, summarization, and hypothesis generation

## What you must configure yourself

This repository does **not** ship with usable credentials, login state, or remote bridge services. To enable the enhanced workflow, you must prepare the following items yourself:

### Required
- `EXA_API_KEY`
- `TAVILY_API_KEY`

### Required for Grok-powered synthesis
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL` (recommended: `auto`)

### Required for restricted-site fallback
- a local Playwright-capable browser environment
- your own login session for IEEE / ACM / Springer / ScienceDirect when needed

### Recommended
- Python 3 available as `python3`
- a private local config file copied from `templates/research.env.example`, such as `templates/research.local.env`

## How Grok access works here

This project does **not** call a native official Grok API directly.

Instead, Grok access is expected to come from **Grok2API**, used as an OpenAI-compatible bridge layer.

Reference:
- https://github.com/chenyme/grok2api

That means:
- you deploy or provide a Grok2API service yourself
- `research-assist` talks to that service through OpenAI-style endpoints
- the backend mainly uses:
  - `GET /v1/models`
  - `POST /v1/chat/completions`

If you do not deploy Grok2API yourself:
- Exa / Tavily / WebSearch / WebFetch / Playwright can still be used
- but Grok-related modes will not work

## Quick start in 3 steps

### 1) Copy the config template

```bash
cp "research-assist/templates/research.env.example" "research-assist/templates/research.local.env"
```

### 2) Fill in your own config

Main variables:
- `EXA_API_KEY`
- `TAVILY_API_KEY`
- `GROK_BRIDGE_BASE_URL`
- `GROK_BRIDGE_API_KEY`
- `GROK_BRIDGE_MODEL=auto`

### 3) Run one aggregation

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --query "multimodal retrieval augmented generation survey" \
  --max-results 5
```

## Common examples

### Check CLI help

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" --help
```

### Idea generation

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-idea \
  --query "efficient multimodal rag for long documents" \
  --max-results 5
```

### Method comparison

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-compare \
  --query "AAA interpolation for electromagnetics" \
  --compare-target "vector fitting" \
  --max-results 5
```

### Claim verification

```bash
python3 "C:/Users/Admin/.cc-switch/skills/research-assist/scripts/research_aggregate.py" \
  --env-file "C:/Users/Admin/.cc-switch/skills/research-assist/templates/research.local.env" \
  --mode think-verify \
  --query "multimodal RAG reliability" \
  --max-results 5
```

## Output highlights

The backend uses an evidence-first schema, including fields such as:

- `results`
- `lanes.search_lane.evidence`
- `lanes.search_lane.playwright_hints`
- `lanes.grok_lane.claims`
- `synthesis.validated_claims`
- `synthesis.disagreements`
- `synthesis.next_queries`

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

## Further reading

See also:
- `references/api-setup.md`
- `references/grok-bridge.md`
- `references/dedup-rules.md`
- `references/login-fallback.md`
- `references/source-priority.md`
- `references/research-report-template.md`

## One-line summary

> A unified, reusable, publishable research skill that brings source discovery, evidence organization, method comparison, idea expansion, claim verification, and restricted-site fallback into one workflow.
