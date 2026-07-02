#!/usr/bin/env python3
"""Validate Product Lens runtime events against a manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_EVENT_FIELDS = ["workflowId", "runId", "stageId", "status", "at", "summary"]
VALID_EVENT_STATUSES = {"waiting", "running", "success", "warning", "error"}
SAFE_META_TYPES = (str, int, float, bool)


def fail(message: str) -> None:
    raise ValueError(message)


def require_string(obj: dict[str, Any], field: str, context: str) -> None:
    if not isinstance(obj.get(field), str) or not obj[field].strip():
        fail(f"{context}.{field} must be a non-empty string")


def manifest_workflow_stages(manifest: dict[str, Any]) -> dict[str, set[str]]:
    workflows = manifest.get("workflows")
    if not isinstance(workflows, list) or not workflows:
        fail("manifest.workflows must be a non-empty list")

    stage_index: dict[str, set[str]] = {}
    for index, workflow in enumerate(workflows):
        if not isinstance(workflow, dict):
            fail(f"workflows[{index}] must be an object")
        require_string(workflow, "id", f"workflows[{index}]")
        stages = workflow.get("stages")
        if not isinstance(stages, list) or not stages:
            fail(f"workflows[{index}].stages must be a non-empty list")
        stage_ids = set()
        for stage_index_value, stage in enumerate(stages):
            if not isinstance(stage, dict):
                fail(f"workflows[{index}].stages[{stage_index_value}] must be an object")
            require_string(stage, "id", f"workflows[{index}].stages[{stage_index_value}]")
            stage_ids.add(stage["id"])
        stage_index[workflow["id"]] = stage_ids
    return stage_index


def validate_event_meta(meta: Any, context: str) -> None:
    if meta is None:
        return
    if not isinstance(meta, dict):
        fail(f"{context}.meta must be an object")
    for key, value in meta.items():
        if not isinstance(key, str) or not key.strip():
            fail(f"{context}.meta keys must be non-empty strings")
        if value is not None and not isinstance(value, SAFE_META_TYPES):
            fail(f"{context}.meta.{key} must be a string, number, boolean, or null")


def validate_runtime_events(manifest: dict[str, Any], events: Any) -> None:
    stage_index = manifest_workflow_stages(manifest)

    if not isinstance(events, list):
        fail("events file must contain a list")

    for index, event in enumerate(events):
        context = f"events[{index}]"
        if not isinstance(event, dict):
            fail(f"{context} must be an object")
        for field in REQUIRED_EVENT_FIELDS:
            require_string(event, field, context)
        if event["status"] not in VALID_EVENT_STATUSES:
            fail(f"{context}.status must be one of {sorted(VALID_EVENT_STATUSES)}")
        workflow_id = event["workflowId"]
        if workflow_id not in stage_index:
            fail(f"{context}.workflowId does not match any manifest workflow: {workflow_id}")
        if event["stageId"] not in stage_index[workflow_id]:
            fail(
                f"{context}.stageId does not match workflow {workflow_id}: {event['stageId']}"
            )
        validate_event_meta(event.get("meta"), context)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Product Lens runtime events.")
    parser.add_argument("manifest", help="Path to product-lens.manifest.json")
    parser.add_argument("events", help="Path to runtime events JSON")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    events = json.loads(Path(args.events).read_text(encoding="utf-8"))
    validate_runtime_events(manifest, events)
    print(f"Runtime events are valid: {args.events}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
