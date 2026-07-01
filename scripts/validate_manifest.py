#!/usr/bin/env python3
"""Validate a Product Lens workflow manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_ROOT_FIELDS = ["product", "workflow", "audience", "stages", "events", "redactionRules"]
REQUIRED_STAGE_FIELDS = ["id", "label", "owner", "whatHappens", "input", "output", "risk"]
VALID_EVENT_STATUSES = {"waiting", "running", "success", "warning", "error"}


def fail(message: str) -> None:
    raise ValueError(message)


def require_string(obj: dict[str, Any], field: str, context: str) -> None:
    if not isinstance(obj.get(field), str) or not obj[field].strip():
        fail(f"{context}.{field} must be a non-empty string")


def validate_manifest(data: dict[str, Any]) -> list[str]:
    warnings: list[str] = []

    for field in REQUIRED_ROOT_FIELDS:
        if field not in data:
            fail(f"Missing root field: {field}")

    for field in ["product", "workflow", "audience"]:
        require_string(data, field, "manifest")

    stages = data["stages"]
    if not isinstance(stages, list) or not stages:
        fail("manifest.stages must be a non-empty list")

    seen_stage_ids: set[str] = set()
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            fail(f"stages[{index}] must be an object")
        for field in REQUIRED_STAGE_FIELDS:
            require_string(stage, field, f"stages[{index}]")
        stage_id = stage["id"]
        if stage_id in seen_stage_ids:
            fail(f"Duplicate stage id: {stage_id}")
        if stage_id.lower() != stage_id or " " in stage_id:
            warnings.append(f"Stage id should be lowercase kebab/snake style: {stage_id}")
        seen_stage_ids.add(stage_id)

    events = data["events"]
    if not isinstance(events, list) or not events:
        fail("manifest.events must be a non-empty list")

    for index, event in enumerate(events):
        if not isinstance(event, dict):
            fail(f"events[{index}] must be an object")
        require_string(event, "name", f"events[{index}]")
        require_string(event, "stageId", f"events[{index}]")
        if event["stageId"] not in seen_stage_ids:
            fail(f"events[{index}].stageId does not match any stage: {event['stageId']}")
        if "status" in event and event["status"] not in VALID_EVENT_STATUSES:
            fail(f"events[{index}].status must be one of {sorted(VALID_EVENT_STATUSES)}")
        if "safeSummary" in event and not isinstance(event["safeSummary"], str):
            fail(f"events[{index}].safeSummary must be a string")

    redaction_rules = data["redactionRules"]
    if not isinstance(redaction_rules, list) or not redaction_rules:
        fail("manifest.redactionRules must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in redaction_rules):
        fail("manifest.redactionRules must contain only non-empty strings")

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Product Lens workflow manifest.")
    parser.add_argument("manifest", help="Path to product-lens.manifest.json")
    args = parser.parse_args()

    path = Path(args.manifest)
    data = json.loads(path.read_text(encoding="utf-8"))
    warnings = validate_manifest(data)

    print(f"Manifest is valid: {path}")
    for warning in warnings:
        print(f"Warning: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
