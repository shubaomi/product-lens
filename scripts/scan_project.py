#!/usr/bin/env python3
"""Scan a project and suggest Product Lens integration points."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


API_PATTERNS = [
    {
        "kind": "route",
        "language": "javascript",
        "pattern": re.compile(r"app\.(get|post|put|patch|delete)\([`'\"]([^`'\"]+)"),
        "method_group": 1,
        "path_group": 2,
    },
    {
        "kind": "route",
        "language": "javascript",
        "pattern": re.compile(r"router\.(get|post|put|patch|delete)\([`'\"]([^`'\"]+)"),
        "method_group": 1,
        "path_group": 2,
    },
    {
        "kind": "fetch",
        "language": "javascript",
        "pattern": re.compile(r"fetch\([`'\"]([^`'\"]+)"),
        "method": "fetch",
        "path_group": 1,
    },
    {
        "kind": "route",
        "language": "python",
        "pattern": re.compile(r"@\w+\.(get|post|put|patch|delete)\([\"']([^\"']+)"),
        "method_group": 1,
        "path_group": 2,
    },
    {
        "kind": "route",
        "language": "python",
        "pattern": re.compile(r"@\w+\.route\([\"']([^\"']+)"),
        "method": "route",
        "path_group": 1,
    },
    {
        "kind": "route",
        "language": "python",
        "pattern": re.compile(r"\b(?:path|re_path)\([\"']([^\"']+)"),
        "method": "django-path",
        "path_group": 1,
    },
    {
        "kind": "route",
        "language": "java",
        "pattern": re.compile(
            r"@(GetMapping|PostMapping|PutMapping|PatchMapping|DeleteMapping|RequestMapping)"
            r"\((?:value\s*=\s*)?[\"']([^\"']+)"
        ),
        "method_group": 1,
        "path_group": 2,
    },
    {
        "kind": "route",
        "language": "java",
        "pattern": re.compile(r"@Path\([\"']([^\"']+)"),
        "method": "jax-rs-path",
        "path_group": 1,
    },
]

EVENT_PATTERNS = [
    "EventSource",
    "text/event-stream",
    "onmessage",
    "WebSocket",
    "ReadableStream",
    "getReader",
    "StreamingResponse",
    "SseEmitter",
    "ServerSentEvent",
    "Flux<",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def detect_framework(root: Path) -> list[str]:
    frameworks: list[str] = []

    package = root / "package.json"
    data = read_text(package) if package.exists() else ""
    for name in ["react", "vite", "next", "express", "vue", "svelte", "fastify"]:
        if f'"{name}"' in data and name not in frameworks:
            frameworks.append(name)

    python_text = "\n".join(
        read_text(root / filename)
        for filename in ["pyproject.toml", "requirements.txt", "Pipfile"]
        if (root / filename).exists()
    )
    for marker, label in [
        ("fastapi", "fastapi"),
        ("flask", "flask"),
        ("django", "django"),
        ("celery", "celery"),
    ]:
        if marker in python_text.lower() and label not in frameworks:
            frameworks.append(label)

    java_text = "\n".join(
        read_text(root / filename)
        for filename in ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"]
        if (root / filename).exists()
    )
    java_markers = {
        "spring-boot": "spring-boot",
        "spring-web": "spring-web",
        "spring-webflux": "spring-webflux",
        "quarkus": "quarkus",
        "micronaut": "micronaut",
    }
    for marker, label in java_markers.items():
        if marker in java_text.lower() and label not in frameworks:
            frameworks.append(label)

    return frameworks


def detect_ui_stack(root: Path) -> list[str]:
    ui_stack: list[str] = []
    package = root / "package.json"
    package_text = read_text(package) if package.exists() else ""

    package_markers = {
        "tailwindcss": "tailwind",
        "@mui/material": "mui",
        "antd": "antd",
        "@chakra-ui/react": "chakra-ui",
        "@mantine/core": "mantine",
        "lucide-react": "lucide-react",
        "class-variance-authority": "class-variance-authority",
        "styled-components": "styled-components",
        "@emotion/react": "emotion",
    }
    for marker, label in package_markers.items():
        if f'"{marker}"' in package_text and label not in ui_stack:
            ui_stack.append(label)

    config_markers = [
        ("tailwind.config.js", "tailwind-config"),
        ("tailwind.config.ts", "tailwind-config"),
        ("components.json", "shadcn-ui"),
    ]
    for filename, label in config_markers:
        if (root / filename).exists() and label not in ui_stack:
            ui_stack.append(label)

    for component_dir in [
        root / "components" / "ui",
        root / "src" / "components" / "ui",
        root / "app" / "components" / "ui",
    ]:
        if component_dir.exists() and "component-library-folder" not in ui_stack:
            ui_stack.append("component-library-folder")

    return ui_stack


def scan_files(root: Path) -> dict:
    candidates = []
    endpoints = []
    streaming_files = []

    ignored_dirs = {"node_modules", ".git", ".venv", "venv", "__pycache__", "dist", "build", "target", ".gradle"}
    supported_suffixes = {".ts", ".tsx", ".js", ".jsx", ".py", ".java"}

    for path in root.rglob("*"):
        if path.is_dir() or any(part in ignored_dirs for part in path.parts):
            continue
        if "skills" in path.parts and "product-lens" in path.parts:
            continue
        if path.suffix.lower() not in supported_suffixes:
            continue

        suffix = path.suffix.lower()
        if suffix in {".ts", ".tsx", ".js", ".jsx"}:
            file_language = "javascript"
        elif suffix == ".py":
            file_language = "python"
        elif suffix == ".java":
            file_language = "java"
        else:
            file_language = "unknown"

        rel = str(path.relative_to(root))
        text = read_text(path)
        if not text:
            continue

        score = 0
        route_tokens = [
            "fetch(",
            "app.post",
            "router.post",
            "@app.",
            "@router.",
            "@GetMapping",
            "@PostMapping",
            "@RequestMapping",
            "@Path(",
        ]
        if any(token in text for token in route_tokens):
            score += 2
        ai_or_stream_tokens = [
            "openai",
            "anthropic",
            "llm",
            "model",
            "stream",
            "SSE",
            "StreamingResponse",
            "SseEmitter",
            "ServerSentEvent",
        ]
        if any(token in text for token in ai_or_stream_tokens):
            score += 2
        lifecycle_tokens = ["onComplete", "onError", "onStatus", "callback", "try:", "catch", "@ExceptionHandler"]
        if any(token in text for token in lifecycle_tokens):
            score += 1
        if score:
            candidates.append({"file": rel, "score": score})

        if any(token in text for token in EVENT_PATTERNS):
            streaming_files.append(rel)

        for pattern_info in API_PATTERNS:
            if pattern_info["language"] != file_language:
                continue
            for match in pattern_info["pattern"].finditer(text):
                method = pattern_info.get("method")
                if pattern_info.get("method_group"):
                    method = match.group(pattern_info["method_group"])
                path_value = match.group(pattern_info["path_group"])
                endpoints.append(
                    {
                        "file": rel,
                        "language": pattern_info["language"],
                        "method_or_call": method,
                        "path": path_value,
                    }
                )

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return {
        "candidateFiles": candidates[:12],
        "endpoints": endpoints[:24],
        "streamingFiles": streaming_files[:12],
    }


def build_recommendations(scan: dict) -> list[str]:
    recommendations = []
    recommendations.append("Adapt Lens UI to the host product's existing layout, controls, typography, and tokens.")
    recommendations.append("Add a Product Lens feature flag and default it off for production.")
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
        "uiStack": detect_ui_stack(root),
        **scan,
        "recommendations": build_recommendations(scan),
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Product Lens scan: {root}")
        print(f"Frameworks: {', '.join(result['frameworks']) or 'unknown'}")
        print(f"UI stack: {', '.join(result['uiStack']) or 'unknown'}")
        print("\nCandidate files:")
        for item in result["candidateFiles"]:
            print(f"- {item['file']} (score {item['score']})")
        print("\nEndpoints/calls:")
        for item in result["endpoints"][:10]:
            language = item.get("language", "unknown")
            print(f"- {item['method_or_call']} {item['path']} ({language}) in {item['file']}")
        print("\nRecommendations:")
        for item in result["recommendations"]:
            print(f"- {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
