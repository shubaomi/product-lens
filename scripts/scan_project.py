#!/usr/bin/env python3
"""Scan a project and suggest Product Lens integration points."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


API_PATTERNS = [
    ("route", re.compile(r"app\.(get|post|put|patch|delete)\([`'\"]([^`'\"]+)")),
    ("route", re.compile(r"router\.(get|post|put|patch|delete)\([`'\"]([^`'\"]+)")),
    ("fetch", re.compile(r"fetch\([`'\"]([^`'\"]+)")),
]

EVENT_PATTERNS = [
    "EventSource",
    "text/event-stream",
    "onmessage",
    "WebSocket",
    "ReadableStream",
    "getReader",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def detect_framework(root: Path) -> list[str]:
    package = root / "package.json"
    if not package.exists():
        return []
    data = read_text(package)
    frameworks = []
    for name in ["react", "vite", "next", "express", "vue", "svelte", "fastify"]:
        if f'"{name}"' in data:
            frameworks.append(name)
    return frameworks


def scan_files(root: Path) -> dict:
    candidates = []
    endpoints = []
    streaming_files = []

    for path in root.rglob("*"):
        if path.is_dir() or any(part in {"node_modules", ".git", "dist", "build"} for part in path.parts):
            continue
        if "skills" in path.parts and "product-lens" in path.parts:
            continue
        if path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx", ".py"}:
            continue

        rel = str(path.relative_to(root))
        text = read_text(path)
        if not text:
            continue

        score = 0
        if any(token in text for token in ["fetch(", "app.post", "router.post", "EventSource", "getReader"]):
            score += 2
        if any(token in text for token in ["openai", "anthropic", "llm", "model", "stream", "SSE"]):
            score += 2
        if any(token in text for token in ["onComplete", "onError", "onStatus", "callback"]):
            score += 1
        if score:
            candidates.append({"file": rel, "score": score})

        if any(token in text for token in EVENT_PATTERNS):
            streaming_files.append(rel)

        for pattern_type, pattern in API_PATTERNS:
            for match in pattern.finditer(text):
                if pattern_type == "fetch":
                    endpoints.append({"file": rel, "method_or_call": "fetch", "path": match.group(1)})
                else:
                    endpoints.append({"file": rel, "method_or_call": match.group(1), "path": match.group(2)})

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return {
        "candidateFiles": candidates[:12],
        "endpoints": endpoints[:24],
        "streamingFiles": streaming_files[:12],
    }


def build_recommendations(scan: dict) -> list[str]:
    recommendations = []
    if scan["streamingFiles"]:
        recommendations.append("Use Pattern A: map existing stream/SSE events to Lens stages.")
    if scan["endpoints"]:
        recommendations.append("Add route-handler milestones around the most important user action.")
    if scan["candidateFiles"]:
        recommendations.append("Start instrumentation in the highest-score candidate files.")
    if not recommendations:
        recommendations.append("Start with a manifest-only Lens page, then add instrumentation later.")
    return recommendations


def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest Product Lens integration points for a project.")
    parser.add_argument("root", nargs="?", default=".", help="Project root to scan")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    scan = scan_files(root)
    result = {
        "root": str(root),
        "frameworks": detect_framework(root),
        **scan,
        "recommendations": build_recommendations(scan),
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Product Lens scan: {root}")
        print(f"Frameworks: {', '.join(result['frameworks']) or 'unknown'}")
        print("\nCandidate files:")
        for item in result["candidateFiles"]:
            print(f"- {item['file']} (score {item['score']})")
        print("\nEndpoints/calls:")
        for item in result["endpoints"][:10]:
            print(f"- {item['method_or_call']} {item['path']} in {item['file']}")
        print("\nRecommendations:")
        for item in result["recommendations"]:
            print(f"- {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
