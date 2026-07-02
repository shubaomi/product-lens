#!/usr/bin/env python3
"""Validate a Product Lens product-level workflow manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_ROOT_FIELDS = ["product", "audience", "workflows", "redactionRules"]
REQUIRED_WORKFLOW_FIELDS = ["id", "label", "description", "stages", "events"]
REQUIRED_STAGE_FIELDS = ["id", "label", "owner", "whatHappens", "input", "output", "risk"]
VALID_EVENT_STATUSES = {"waiting", "running", "success", "warning", "error"}


def fail(message: str) -> None:
    raise ValueError(message)


def require_string(obj: dict[str, Any], field: str, context: str) -> None:
    if not isinstance(obj.get(field), str) or not obj[field].strip():
        fail(f"{context}.{field} must be a non-empty string")


def require_id(value: str, context: str, warnings: list[str]) -> None:
    if value.lower() != value or " " in value:
        warnings.append(f"{context} should be lowercase kebab/snake style: {value}")


def validate_events(events: Any, stage_ids: set[str], context: str) -> None:
    if not isinstance(events, list) or not events:
        fail(f"{context}.events must be a non-empty list")

    for index, event in enumerate(events):
        event_context = f"{context}.events[{index}]"
        if not isinstance(event, dict):
            fail(f"{event_context} must be an object")
        require_string(event, "name", event_context)
        require_string(event, "stageId", event_context)
        if event["stageId"] not in stage_ids:
            fail(f"{event_context}.stageId does not match any stage: {event['stageId']}")
        if "status" in event and event["status"] not in VALID_EVENT_STATUSES:
            fail(f"{event_context}.status must be one of {sorted(VALID_EVENT_STATUSES)}")
        if "safeSummary" in event and not isinstance(event["safeSummary"], str):
            fail(f"{event_context}.safeSummary must be a string")


def validate_workflow(workflow: dict[str, Any], index: int, warnings: list[str]) -> None:
    context = f"workflows[{index}]"
    for field in REQUIRED_WORKFLOW_FIELDS:
        if field not in workflow:
            fail(f"Missing {context}.{field}")

    for field in ["id", "label", "description"]:
        require_string(workflow, field, context)
    require_id(workflow["id"], f"{context}.id", warnings)

    entrypoints = workflow.get("entrypoints", [])
    if entrypoints and (
        not isinstance(entrypoints, list)
        or not all(isinstance(item, str) and item.strip() for item in entrypoints)
    ):
        fail(f"{context}.entrypoints must contain only non-empty strings")

    stages = workflow["stages"]
    if not isinstance(stages, list) or not stages:
        fail(f"{context}.stages must be a non-empty list")

    seen_stage_ids: set[str] = set()
    for stage_index, stage in enumerate(stages):
        stage_context = f"{context}.stages[{stage_index}]"
        if not isinstance(stage, dict):
            fail(f"{stage_context} must be an object")
        for field in REQUIRED_STAGE_FIELDS:
            require_string(stage, field, stage_context)
        stage_id = stage["id"]
        if stage_id in seen_stage_ids:
            fail(f"Duplicate stage id in {context}: {stage_id}")
        require_id(stage_id, f"{stage_context}.id", warnings)
        seen_stage_ids.add(stage_id)

    validate_events(workflow["events"], seen_stage_ids, context)


def validate_manifest(data: dict[str, Any]) -> list[str]:
    warnings: list[str] = []

    if "workflows" not in data and all(field in data for field in ["workflow", "stages", "events"]):
        warnings.append("Legacy single-workflow manifest detected. Prefer product-lens.v2 with workflows[].")
        data = {
            "product": data.get("product"),
            "audience": data.get("audience"),
            "redactionRules": data.get("redactionRules"),
            "workflows": [
                {
                    "id": "default-workflow",
                    "label": data.get("workflow"),
                    "description": data.get("workflow"),
                    "stages": data.get("stages"),
                    "events": data.get("events"),
                }
            ],
        }

    for field in REQUIRED_ROOT_FIELDS:
        if field not in data:
            fail(f"Missing root field: {field}")

    for field in ["product", "audience"]:
        require_string(data, field, "manifest")

    schema_version = data.get("schemaVersion")
    if schema_version and schema_version != "product-lens.v2":
        warnings.append(f"Unknown schemaVersion: {schema_version}")

    workflows = data["workflows"]
    if not isinstance(workflows, list) or not workflows:
        fail("manifest.workflows must be a non-empty list")

    seen_workflow_ids: set[str] = set()
    for index, workflow in enumerate(workflows):
        if not isinstance(workflow, dict):
            fail(f"workflows[{index}] must be an object")
        validate_workflow(workflow, index, warnings)
        workflow_id = workflow["id"]
        if workflow_id in seen_workflow_ids:
            fail(f"Duplicate workflow id: {workflow_id}")
        seen_workflow_ids.add(workflow_id)

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
