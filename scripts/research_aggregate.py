#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List


DEFAULT_EXA_BASE = "https://api.exa.ai"
DEFAULT_TAVILY_BASE = "https://api.tavily.com"
DEFAULT_GROK_MODEL = "grok-4.1-fast"
PAYWALL_HINT_DOMAINS = {
    "ieeexplore.ieee.org",
    "dl.acm.org",
    "link.springer.com",
    "sciencedirect.com",
    "onlinelibrary.wiley.com",
    "nature.com",
}


def load_env_file(file_path: str) -> None:
    if not file_path:
        return
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    with open(file_path, "r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                continue
            if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
                value = value[1:-1]
            if key not in os.environ:
                os.environ[key] = value


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def normalize_base_url(url: str) -> str:
    return (url or "").rstrip("/")


def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlparse(url)
    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
    filtered = []
    for key, value in query_pairs:
        key_lower = key.lower()
        if key_lower.startswith("utm_") or key_lower in {"ref", "ref_src", "source", "si"}:
            continue
        filtered.append((key, value))
    filtered_query = urllib.parse.urlencode(filtered, doseq=True)
    return urllib.parse.urlunparse(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            filtered_query,
            "",
        )
    )


def normalize_title(title: str) -> str:
    if not title:
        return ""
    lowered = title.lower().strip()
    chars = []
    for ch in lowered:
        if ch.isalnum() or ch.isspace():
            chars.append(ch)
        else:
            chars.append(" ")
    return " ".join("".join(chars).split())


def extract_arxiv_id(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlparse(url)
    if "arxiv.org" not in parsed.netloc.lower():
        return ""
    path = parsed.path.strip("/")
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] in {"abs", "pdf"}:
        value = parts[1]
        if value.endswith(".pdf"):
            value = value[:-4]
        return value
    return ""


def guess_doi(url: str, metadata: Dict[str, Any]) -> str:
    for key in ("doi", "DOI"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    if url and "doi.org/" in url:
        return url.split("doi.org/", 1)[1].strip("/")
    return ""


def post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: int) -> Dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    for key, value in headers.items():
        if value:
            req.add_header(key, value)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        if not raw.strip():
            return {}
        return json.loads(raw)


def get_json(url: str, headers: Dict[str, str], timeout: int) -> Dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    for key, value in headers.items():
        if value:
            req.add_header(key, value)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        if not raw.strip():
            return {}
        return json.loads(raw)


def resolve_grok_model(base: str, api_key: str, configured_model: str, timeout: int) -> str:
    configured = (configured_model or "").strip()
    if configured and configured.lower() not in {"auto"}:
        return configured

    headers: Dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    model_ids: List[str] = []
    try:
        data = get_json(f"{base}/models", headers, timeout)
        for item in data.get("data") or []:
            if isinstance(item, dict):
                model_id = item.get("id")
                if isinstance(model_id, str) and model_id.strip():
                    model_ids.append(model_id.strip())
    except Exception:
        model_ids = []

    preferred = [
        "grok-4.20-auto",
        "grok-4.20-fast",
        "grok-4.20-0309-non-reasoning",
        "grok-4.20-0309",
        "grok-4.20-0309-reasoning",
    ]
    for model_id in preferred:
        if model_id in model_ids:
            return model_id

    for model_id in model_ids:
        lower = model_id.lower()
        if "image" in lower:
            continue
        return model_id

    return configured or DEFAULT_GROK_MODEL


def safe_error(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        if body:
            return f"HTTP {exc.code}: {body[:300]}"
        return f"HTTP {exc.code}"
    return str(exc)


def map_exa_results(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_results = data.get("results") or []
    mapped = []
    for item in raw_results:
        if not isinstance(item, dict):
            continue
        url = item.get("url") or item.get("id") or ""
        title = item.get("title") or ""
        text = item.get("text") or ""
        highlights = item.get("highlights") or []
        snippet = text[:600] if isinstance(text, str) else ""
        if not snippet and isinstance(highlights, list):
            snippet = " ".join(str(x) for x in highlights[:3])[:600]
        author = item.get("author") or item.get("authors")
        metadata = {
            "publishedDate": item.get("publishedDate"),
            "author": author,
            "score": item.get("score"),
            "highlights": highlights,
        }
        mapped.append(
            {
                "source": "exa",
                "title": title,
                "url": url,
                "canonical_url": canonicalize_url(url),
                "snippet": snippet,
                "published": item.get("publishedDate"),
                "metadata": metadata,
                "doi": guess_doi(url, item),
                "arxiv_id": extract_arxiv_id(url),
                "normalized_title": normalize_title(title),
            }
        )
    return mapped


def map_tavily_results(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_results = data.get("results") or []
    mapped = []
    for item in raw_results:
        if not isinstance(item, dict):
            continue
        url = item.get("url") or ""
        title = item.get("title") or ""
        mapped.append(
            {
                "source": "tavily",
                "title": title,
                "url": url,
                "canonical_url": canonicalize_url(url),
                "snippet": (item.get("content") or item.get("snippet") or "")[:600],
                "published": item.get("published_date") or item.get("publishedDate"),
                "metadata": {
                    "score": item.get("score"),
                    "raw_content": item.get("raw_content"),
                },
                "doi": guess_doi(url, item),
                "arxiv_id": extract_arxiv_id(url),
                "normalized_title": normalize_title(title),
            }
        )
    return mapped


def exa_search(query: str, max_results: int, timeout: int) -> Dict[str, Any]:
    api_key = env("EXA_API_KEY")
    if not api_key:
        return {"ok": False, "source": "exa", "error": "EXA_API_KEY is not set", "results": []}
    base = normalize_base_url(env("EXA_API_BASE", DEFAULT_EXA_BASE))
    payload = {
        "query": query,
        "numResults": max_results,
        "contents": {"text": True, "highlights": {"numSentences": 3}},
    }
    try:
        data = post_json(
            f"{base}/search",
            payload,
            {"x-api-key": api_key, "User-Agent": "curl/8.0"},
            timeout,
        )
        return {"ok": True, "source": "exa", "results": map_exa_results(data), "raw": data}
    except Exception as exc:
        return {"ok": False, "source": "exa", "error": safe_error(exc), "results": []}


def tavily_search(query: str, max_results: int, timeout: int) -> Dict[str, Any]:
    api_key = env("TAVILY_API_KEY")
    if not api_key:
        return {"ok": False, "source": "tavily", "error": "TAVILY_API_KEY is not set", "results": []}
    base = normalize_base_url(env("TAVILY_API_BASE", DEFAULT_TAVILY_BASE))
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False,
    }
    try:
        data = post_json(
            f"{base}/search",
            payload,
            {},
            timeout,
        )
        return {"ok": True, "source": "tavily", "results": map_tavily_results(data), "raw": data}
    except Exception as exc:
        return {"ok": False, "source": "tavily", "error": safe_error(exc), "results": []}


def grok_query_suggestions(query: str, timeout: int) -> Dict[str, Any]:
    base = normalize_base_url(env("GROK_BRIDGE_BASE_URL"))
    if not base:
        return {"ok": False, "source": "grok", "error": "GROK_BRIDGE_BASE_URL is not set", "suggestions": []}
    api_key = env("GROK_BRIDGE_API_KEY")
    configured_model = env("GROK_BRIDGE_MODEL", DEFAULT_GROK_MODEL)
    model = resolve_grok_model(base, api_key, configured_model, timeout)
    prompt = (
        "You are helping with academic literature discovery. "
        "Given a research topic, return JSON with keys queries and angles. "
        "queries must be 5-8 short search queries in English optimized for finding papers, surveys, benchmarks, code, and recent work. "
        "angles must be 3-5 short research subtopics. "
        "Return JSON only."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        "temperature": 0.2,
        "stream": False,
    }
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    try:
        data = post_json(
            f"{base}/chat/completions",
            payload,
            headers,
            timeout,
        )
        text = ""
        choices = data.get("choices") or []
        if choices and isinstance(choices[0], dict):
            message = choices[0].get("message") or {}
            text = message.get("content") or ""
        parsed = parse_json_text(text)
        suggestions = parsed.get("queries") if isinstance(parsed, dict) else []
        angles = parsed.get("angles") if isinstance(parsed, dict) else []
        if not isinstance(suggestions, list):
            suggestions = []
        if not isinstance(angles, list):
            angles = []
        return {
            "ok": True,
            "source": "grok",
            "suggestions": [str(x) for x in suggestions],
            "angles": [str(x) for x in angles],
            "raw": data,
        }
    except Exception as exc:
        return {"ok": False, "source": "grok", "error": safe_error(exc), "suggestions": [], "angles": []}


def url_hostname(url: str) -> str:
    if not is_http_url(url):
        return ""
    try:
        return urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ""


def should_playwright_fetch(url: str) -> bool:
    host = url_hostname(url)
    if not host:
        return False
    for domain in PAYWALL_HINT_DOMAINS:
        if host == domain or host.endswith(f".{domain}"):
            return True
    return False


def build_playwright_hints(evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    hints: List[Dict[str, Any]] = []
    seen = set()
    for item in evidence:
        url = str(item.get("url") or "").strip()
        canonical = canonicalize_url(url)
        if not canonical or canonical in seen:
            continue
        if not should_playwright_fetch(url):
            continue
        seen.add(canonical)
        hints.append(
            {
                "url": url,
                "hostname": url_hostname(url),
                "reason": "likely_login_or_paywall",
                "suggested_action": "playwright_fetch_metadata",
            }
        )
    return hints


def parse_json_text(text: str) -> Dict[str, Any]:
    if not text:
        return {}
    raw = text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines:
            lines = lines[1:]
        while lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    except Exception:
        pass

    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        maybe = raw[start : end + 1]
        try:
            parsed = json.loads(maybe)
            return parsed if isinstance(parsed, dict) else {"value": parsed}
        except Exception:
            return {"raw_text": text}
    return {"raw_text": text}


def is_http_url(url: str) -> bool:
    if not isinstance(url, str):
        return False
    lowered = url.strip().lower()
    return lowered.startswith("http://") or lowered.startswith("https://")


def normalize_evidence_items(items: Any, fallback_source: str) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    if not isinstance(items, list):
        return normalized
    for item in items:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not is_http_url(url):
            continue
        title = str(item.get("title") or "").strip()
        snippet = str(item.get("snippet") or item.get("note") or "").strip()[:600]
        source = str(item.get("source") or fallback_source or "grok_web").strip()
        normalized.append(
            {
                "title": title,
                "url": url,
                "canonical_url": canonicalize_url(url),
                "source": source,
                "snippet": snippet,
            }
        )
    return normalized


def grok_think_analysis(query: str, mode: str, compare_target: str, max_claims: int, timeout: int) -> Dict[str, Any]:
    base = normalize_base_url(env("GROK_BRIDGE_BASE_URL"))
    if not base:
        return {
            "ok": False,
            "source": "grok_think",
            "error": "GROK_BRIDGE_BASE_URL is not set",
            "claims": [],
            "disagreements": [],
            "next_queries": [],
        }

    api_key = env("GROK_BRIDGE_API_KEY")
    configured_model = env("GROK_BRIDGE_MODEL", DEFAULT_GROK_MODEL)
    model = resolve_grok_model(base, api_key, configured_model, timeout)

    mode_goal_map = {
        "think-idea": "Generate new and testable research ideas, not generic statements.",
        "think-compare": "Compare approaches, assumptions, and reported outcomes; highlight disagreements.",
        "think-verify": "Verify major claims and prioritize reproducibility risks and uncertainty.",
    }
    mode_goal = mode_goal_map.get(mode, "Analyze and synthesize research evidence.")
    compare_clause = f" Compare target: {compare_target}." if compare_target else ""

    prompt = (
        "You are a research synthesis assistant with web-search capability. "
        f"Mode: {mode}. {mode_goal}{compare_clause} "
        "Return strict JSON only with keys: lane, claims, disagreements, next_queries. "
        f"claims must be an array (max {max_claims}) of objects with keys: claim, confidence, evidence, note. "
        "confidence must be one of low/medium/high. "
        "Each evidence item must include title, url, source, snippet. "
        "Do not include evidence entries without valid http/https URLs. "
        "disagreements must be an array of objects: topic, lane_a, lane_b, status. "
        "next_queries must be 3-8 concise English queries for next search round."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        "temperature": 0.2,
        "stream": False,
    }
    headers: Dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        data = post_json(f"{base}/chat/completions", payload, headers, timeout)
        text = ""
        choices = data.get("choices") or []
        if choices and isinstance(choices[0], dict):
            message = choices[0].get("message") or {}
            text = message.get("content") or ""

        parsed = parse_json_text(text)
        raw_claims = parsed.get("claims") if isinstance(parsed, dict) else []
        raw_disagreements = parsed.get("disagreements") if isinstance(parsed, dict) else []
        raw_next_queries = parsed.get("next_queries") if isinstance(parsed, dict) else []

        claims: List[Dict[str, Any]] = []
        if isinstance(raw_claims, list):
            for item in raw_claims[: max(1, max_claims)]:
                if not isinstance(item, dict):
                    continue
                claim = str(item.get("claim") or "").strip()
                if not claim:
                    continue
                confidence = str(item.get("confidence") or "medium").strip().lower()
                if confidence not in {"low", "medium", "high"}:
                    confidence = "medium"
                evidence = normalize_evidence_items(item.get("evidence"), "grok_web")
                note = str(item.get("note") or "").strip()
                claims.append(
                    {
                        "claim": claim,
                        "confidence": confidence,
                        "note": note,
                        "evidence": evidence,
                    }
                )

        disagreements: List[Dict[str, Any]] = []
        if isinstance(raw_disagreements, list):
            for item in raw_disagreements:
                if not isinstance(item, dict):
                    continue
                topic = str(item.get("topic") or "").strip()
                if not topic:
                    continue
                disagreements.append(
                    {
                        "topic": topic,
                        "lane_a": str(item.get("lane_a") or "").strip(),
                        "lane_b": str(item.get("lane_b") or "").strip(),
                        "status": str(item.get("status") or "uncertain").strip(),
                    }
                )

        next_queries: List[str] = []
        if isinstance(raw_next_queries, list):
            for item in raw_next_queries:
                value = str(item).strip()
                if value:
                    next_queries.append(value)

        return {
            "ok": True,
            "source": "grok_think",
            "mode": mode,
            "model": model,
            "claims": claims,
            "disagreements": disagreements,
            "next_queries": next_queries,
            "raw": data,
        }
    except Exception as exc:
        return {
            "ok": False,
            "source": "grok_think",
            "error": safe_error(exc),
            "claims": [],
            "disagreements": [],
            "next_queries": [],
        }


def dedupe_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = {}
    for item in results:
        doi = item.get("doi") or ""
        arxiv_id = item.get("arxiv_id") or ""
        normalized_title = item.get("normalized_title") or ""
        canonical_url = item.get("canonical_url") or ""
        if doi:
            key = f"doi:{doi.lower()}"
        elif arxiv_id:
            key = f"arxiv:{arxiv_id.lower()}"
        elif normalized_title:
            key = f"title:{normalized_title}"
        else:
            key = f"url:{canonical_url or item.get('url') or ''}"

        existing = grouped.get(key)
        if not existing:
            grouped[key] = {
                "canonical_title": item.get("title") or "",
                "normalized_title": normalized_title,
                "doi": doi,
                "arxiv_id": arxiv_id,
                "published": item.get("published"),
                "canonical_source": item.get("source"),
                "canonical_url": item.get("url"),
                "snippet": item.get("snippet") or "",
                "sources": [
                    {
                        "source": item.get("source"),
                        "title": item.get("title"),
                        "url": item.get("url"),
                    }
                ],
            }
            continue

        existing["sources"].append(
            {
                "source": item.get("source"),
                "title": item.get("title"),
                "url": item.get("url"),
            }
        )
        if not existing.get("doi") and doi:
            existing["doi"] = doi
        if not existing.get("arxiv_id") and arxiv_id:
            existing["arxiv_id"] = arxiv_id
        if len(item.get("snippet") or "") > len(existing.get("snippet") or ""):
            existing["snippet"] = item.get("snippet") or existing.get("snippet")
        if existing.get("canonical_source") not in {"exa", "tavily"} and item.get("source") in {"exa", "tavily"}:
            existing["canonical_source"] = item.get("source")
            existing["canonical_url"] = item.get("url")
        if not existing.get("canonical_title") and item.get("title"):
            existing["canonical_title"] = item.get("title")
    return list(grouped.values())


def build_search_evidence(deduped: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    evidence: List[Dict[str, Any]] = []
    for item in deduped:
        url = str(item.get("canonical_url") or "").strip()
        if not is_http_url(url):
            continue
        evidence.append(
            {
                "title": str(item.get("canonical_title") or "").strip(),
                "url": url,
                "canonical_url": canonicalize_url(url),
                "source": str(item.get("canonical_source") or "search").strip(),
                "snippet": str(item.get("snippet") or "")[:600],
                "published": item.get("published"),
                "doi": item.get("doi") or "",
                "arxiv_id": item.get("arxiv_id") or "",
            }
        )
    return evidence


def build_evidence_url_set(evidence: List[Dict[str, Any]]) -> set:
    values = set()
    for item in evidence:
        canonical = item.get("canonical_url") or ""
        url = item.get("url") or ""
        if canonical:
            values.add(canonical)
        elif url:
            values.add(canonicalize_url(url))
    return values


def validate_claims_against_search(claims: List[Dict[str, Any]], search_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    known_urls = build_evidence_url_set(search_evidence)
    validated: List[Dict[str, Any]] = []

    for claim in claims:
        evidence = claim.get("evidence") or []
        matched = []
        unmatched = []
        for ev in evidence:
            canonical = ev.get("canonical_url") or canonicalize_url(ev.get("url") or "")
            if canonical and canonical in known_urls:
                matched.append(ev)
            else:
                unmatched.append(ev)

        if evidence and len(matched) == len(evidence):
            support = "supported"
        elif matched:
            support = "partial"
        else:
            support = "unverified"

        validated.append(
            {
                "claim": claim.get("claim"),
                "confidence": claim.get("confidence"),
                "note": claim.get("note"),
                "support": support,
                "matched_evidence": matched,
                "unmatched_evidence": unmatched,
                "evidence": evidence,
            }
        )

    return validated


def merge_next_queries(primary: List[str], secondary: List[str]) -> List[str]:
    merged: List[str] = []
    seen = set()
    for value in list(primary or []) + list(secondary or []):
        text = str(value).strip()
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        merged.append(text)
    return merged


def emit_json(data: Dict[str, Any]) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    try:
        sys.stdout.write(text + "\n")
    except UnicodeEncodeError:
        sys.stdout.write(json.dumps(data, ensure_ascii=True, indent=2) + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Academic research search aggregator")
    parser.add_argument("--query", required=True, help="Research query")
    parser.add_argument("--max-results", type=int, default=5, help="Max results per source")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    parser.add_argument("--sources", nargs="*", choices=["exa", "tavily", "grok"], help="Sources to call; defaults to all configured")
    parser.add_argument("--env-file", help="Optional .env file to load before making requests")
    parser.add_argument("--include-raw", action="store_true", help="Include raw API payloads")
    parser.add_argument(
        "--mode",
        choices=["aggregate", "think-idea", "think-compare", "think-verify"],
        default="aggregate",
        help="aggregate=search aggregation only; think-* enables dual-lane synthesis",
    )
    parser.add_argument("--compare-target", default="", help="Second target used by think-compare mode")
    parser.add_argument("--max-claims", type=int, default=8, help="Maximum Grok claims to keep in think modes")
    return parser.parse_args()


def run_aggregate_mode(args: argparse.Namespace) -> Dict[str, Any]:
    requested = set(args.sources or ["exa", "tavily", "grok"])

    source_reports: List[Dict[str, Any]] = []
    flat_results: List[Dict[str, Any]] = []
    suggestions: Dict[str, Any] = {"queries": [], "angles": []}

    if "exa" in requested:
        report = exa_search(args.query, args.max_results, args.timeout)
        source_reports.append(report if args.include_raw else {k: v for k, v in report.items() if k != "raw"})
        flat_results.extend(report.get("results") or [])

    if "tavily" in requested:
        report = tavily_search(args.query, args.max_results, args.timeout)
        source_reports.append(report if args.include_raw else {k: v for k, v in report.items() if k != "raw"})
        flat_results.extend(report.get("results") or [])

    if "grok" in requested:
        report = grok_query_suggestions(args.query, args.timeout)
        source_reports.append(report if args.include_raw else {k: v for k, v in report.items() if k != "raw"})
        suggestions = {
            "queries": report.get("suggestions") or [],
            "angles": report.get("angles") or [],
        }

    deduped = dedupe_results(flat_results)
    return {
        "ok": any(report.get("ok") for report in source_reports),
        "mode": "aggregate",
        "query": args.query,
        "requested_sources": sorted(requested),
        "configured": {
            "exa": bool(env("EXA_API_KEY")),
            "tavily": bool(env("TAVILY_API_KEY")),
            "grok_bridge": bool(env("GROK_BRIDGE_BASE_URL")),
        },
        "source_reports": source_reports,
        "query_expansion": suggestions,
        "results": deduped,
        "result_count": len(deduped),
        "generated_at": now_iso(),
    }


def run_think_mode(args: argparse.Namespace) -> Dict[str, Any]:
    requested = set(args.sources or ["exa", "tavily", "grok"])

    source_reports: List[Dict[str, Any]] = []
    flat_results: List[Dict[str, Any]] = []
    expansion_suggestions: Dict[str, Any] = {"queries": [], "angles": []}

    if "exa" in requested:
        report = exa_search(args.query, args.max_results, args.timeout)
        source_reports.append(report if args.include_raw else {k: v for k, v in report.items() if k != "raw"})
        flat_results.extend(report.get("results") or [])

    if "tavily" in requested:
        report = tavily_search(args.query, args.max_results, args.timeout)
        source_reports.append(report if args.include_raw else {k: v for k, v in report.items() if k != "raw"})
        flat_results.extend(report.get("results") or [])

    grok_query_report: Dict[str, Any] = {
        "ok": False,
        "source": "grok",
        "suggestions": [],
        "angles": [],
        "error": "grok not requested",
    }
    grok_think_report: Dict[str, Any] = {
        "ok": False,
        "source": "grok_think",
        "claims": [],
        "disagreements": [],
        "next_queries": [],
        "error": "grok not requested",
    }

    if "grok" in requested:
        grok_query_report = grok_query_suggestions(args.query, args.timeout)
        source_reports.append(grok_query_report if args.include_raw else {k: v for k, v in grok_query_report.items() if k != "raw"})
        expansion_suggestions = {
            "queries": grok_query_report.get("suggestions") or [],
            "angles": grok_query_report.get("angles") or [],
        }

        grok_think_report = grok_think_analysis(
            query=args.query,
            mode=args.mode,
            compare_target=args.compare_target,
            max_claims=args.max_claims,
            timeout=args.timeout,
        )
        source_reports.append(grok_think_report if args.include_raw else {k: v for k, v in grok_think_report.items() if k != "raw"})

    deduped = dedupe_results(flat_results)
    search_evidence = build_search_evidence(deduped)
    playwright_hints = build_playwright_hints(search_evidence)
    validated_claims = validate_claims_against_search(grok_think_report.get("claims") or [], search_evidence)

    auto_disagreements = []
    for claim in validated_claims:
        if claim.get("support") == "unverified" and (claim.get("evidence") or []):
            auto_disagreements.append(
                {
                    "topic": claim.get("claim"),
                    "lane_a": "grok_web",
                    "lane_b": "search_lane",
                    "status": "unverified_by_exa_tavily",
                }
            )

    all_disagreements = (grok_think_report.get("disagreements") or []) + auto_disagreements
    next_queries = merge_next_queries(
        grok_think_report.get("next_queries") or [],
        expansion_suggestions.get("queries") or [],
    )

    supported_count = sum(1 for item in validated_claims if item.get("support") == "supported")
    partial_count = sum(1 for item in validated_claims if item.get("support") == "partial")
    unverified_count = sum(1 for item in validated_claims if item.get("support") == "unverified")

    return {
        "ok": any(report.get("ok") for report in source_reports),
        "mode": args.mode,
        "query": args.query,
        "compare_target": args.compare_target,
        "requested_sources": sorted(requested),
        "configured": {
            "exa": bool(env("EXA_API_KEY")),
            "tavily": bool(env("TAVILY_API_KEY")),
            "grok_bridge": bool(env("GROK_BRIDGE_BASE_URL")),
        },
        "source_reports": source_reports,
        "lanes": {
            "search_lane": {
                "evidence_count": len(search_evidence),
                "evidence": search_evidence,
                "playwright_hints": playwright_hints,
            },
            "grok_lane": {
                "query_expansion": expansion_suggestions,
                "claims": grok_think_report.get("claims") or [],
            },
        },
        "synthesis": {
            "validated_claims": validated_claims,
            "disagreements": all_disagreements,
            "next_queries": next_queries,
            "support_summary": {
                "supported": supported_count,
                "partial": partial_count,
                "unverified": unverified_count,
            },
        },
        "results": deduped,
        "result_count": len(deduped),
        "generated_at": now_iso(),
    }


def main() -> int:
    args = parse_args()
    if args.env_file:
        load_env_file(args.env_file)

    if args.mode == "aggregate":
        output = run_aggregate_mode(args)
    else:
        output = run_think_mode(args)

    emit_json(output)
    return 0 if output.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
