---
name: product-lens
description: "Build a standalone Product Lens for existing products: a safe, dynamic, sidecar workflow explainer that shows how a product feature, AI workflow, request pipeline, SaaS module, or internal tool works step by step without embedding into or rewriting the core business surface. Use when a user asks to add a /lens or /how-it-works page, instrument staged events, create a workflow manifest, visualize live request execution, generate a replayable trace, or package a product transparency layer for demos, onboarding, hackathons, open source distribution, or non-technical stakeholder education."
---

# Product Lens

Product Lens is a standalone transparency layer for a working product. It maps one important user action into safe stages, instruments lightweight runtime events, and renders a separate Lens page, drawer, route, or companion app that helps non-technical users understand what happens inside the product.

Default to an independent Lens surface. Do not place the Lens inside the primary business result page unless the user explicitly asks for an inline variant.

## Core Workflow

1. Pick one core workflow users care about.
2. Run `scripts/scan_project.py <project-root>` to find likely API routes, stream handlers, model calls, and frontend callbacks.
3. Create a workflow manifest with stages, owners, safe inputs, safe outputs, risks, and event names.
4. Add non-invasive instrumentation at existing lifecycle boundaries.
5. Render the Lens on a separate page, drawer, route, or companion app.
6. Verify a real request lights up stages one by one.
7. Check that no secrets, raw prompts, credentials, full request bodies, or personal data are displayed.

## Use The Bundled Resources

- Run `scripts/scan_project.py <project-root> --json` before choosing integration points.
- Run `scripts/validate_manifest.py <manifest.json>` after creating or editing a manifest.
- Read `references/integration-patterns.md` when choosing an instrumentation approach.
- Read `references/safety-rules.md` before exposing event metadata in any UI.
- Copy/adapt `assets/react/ProductLensPanel.tsx` for React products.
- Start from `assets/product-lens-manifest.example.json` or `examples/explainit/product-lens.manifest.json`.

## Product Lens Contract

The Lens must be removable. The original feature should keep working if all Lens UI and event listeners are disabled.

Use this contract:

- `manifest`: static description of the workflow.
- `events`: runtime facts emitted by the product.
- `Lens UI`: separate observer surface that combines manifest and events.

Events should include:

- `stageId`: stable id from the manifest.
- `status`: `waiting`, `running`, `success`, `warning`, or `error`.
- `at`: timestamp.
- `summary`: safe plain-language summary.
- `meta`: optional safe counts, durations, provider labels, retry state, cache state, or redacted ids.

## Instrumentation Rules

- Prefer existing lifecycle boundaries: form submit, route handler start, cache hit, model call start/end, queue job start/end, SSE event, webhook event, render completion.
- Keep instrumentation append-only and removable. Do not change business behavior to support Lens.
- Emit timestamps and stage ids. Avoid full payloads.
- Use safe metadata such as item counts, durations, provider names, retry state, cache hit/miss, or redacted labels.
- For AI products, show model-call phases and output categories, not raw prompts, system messages, API keys, or private user text.
- For production, prefer live events or replayed trace events over a static full blueprint. Static manifest-only mode is acceptable only for planning, docs, or demos without a running app.

## UI Rules

Use one of these surfaces:

- Dedicated route: `/lens`, `/how-it-works`, `/trace`, or `/workflow`.
- Sidecar drawer that opens beside the product without covering the primary task.
- Separate internal/dev companion page.
- Replay viewer for a saved trace.

The UI should show:

- Current workflow name and run status.
- Ordered stage timeline.
- Stage owner and safe explanation.
- Incremental event arrival, with timestamps or elapsed time.
- Degraded/error states that explain what stayed usable.
- Short safety note that the Lens exposes summaries only.

Avoid:

- Embedding the Lens directly inside the core business result.
- Showing all stages as complete before a request actually runs.
- Displaying secrets, prompts, tokens, full bodies, or personal data.
- Turning implementation trivia into user-facing noise.

## Validation Checklist

- The original feature works with Lens disabled.
- The Lens lives on a separate surface unless inline mode was explicitly requested.
- At least one real run lights up stages sequentially.
- Empty, running, success, degraded, and error states are understandable.
- Manifest validation passes.
- No API keys, raw prompts, auth tokens, environment values, full request bodies, or personal data are exposed.
- A non-technical viewer can explain the workflow after watching the Lens for 30 seconds.
