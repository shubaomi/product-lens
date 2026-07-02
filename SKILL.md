---
name: product-lens
description: "Build a standalone, language-agnostic Product Lens for existing products: a safe, dynamic, sidecar workflow explainer that can describe one or many core product workflows step by step without embedding into or rewriting the core business surface. Use when a user asks to add a /lens or /how-it-works page, instrument staged workflow events, create a product-level workflow manifest, visualize live request execution, generate replayable traces, compare multiple feature flows, or package a product transparency layer for demos, onboarding, hackathons, open source distribution, or non-technical stakeholder education across JavaScript/TypeScript, Python, Java, or other product stacks."
---

# Product Lens

Product Lens is a standalone transparency layer for a working product. It maps one or more important product workflows into safe stages, instruments lightweight runtime events, and renders a separate Lens page, drawer, route, or companion app that helps non-technical users understand what happens inside the product.

Default to an independent Lens surface. Do not place the Lens inside the primary business result page unless the user explicitly asks for an inline variant.

## Core Workflow

1. Inventory the product's core workflows. Do not assume the product has only one important flow.
2. Run `scripts/scan_project.py <project-root>` to find likely API routes, stream handlers, model calls, and frontend callbacks.
3. Inspect the host product's UI system: layout shell, typography, spacing, controls, icons, CSS variables, component library, and route/navigation patterns.
4. Create a product-level manifest with `workflows[]`. Each workflow needs a stable `id`, stages, owners, safe inputs, safe outputs, risks, and event names.
5. Add a feature flag or environment switch. Product Lens should be disabled by default in production unless the user explicitly wants a public transparency page.
6. Add non-invasive instrumentation at existing lifecycle boundaries.
7. Emit events with `workflowId`, `runId`, `stageId`, `status`, `at`, `summary`, and optional safe `meta`.
8. Render the Lens on a separate page, drawer, route, or companion app with workflow/run selection when multiple workflows exist.
9. Verify a real request lights up stages one by one for each instrumented workflow.
10. Check that no secrets, raw prompts, credentials, full request bodies, or personal data are displayed.

## Use The Bundled Resources

- Run `scripts/scan_project.py <project-root> --json` before choosing integration points. Use its framework and `uiStack` signals to reuse the host product's UI system.
- Run `scripts/validate_manifest.py <manifest.json>` after creating or editing a manifest.
- Run `scripts/validate_events.py <manifest.json> <events.json>` when sample or replay events are available.
- Read `references/integration-patterns.md` when choosing an instrumentation approach.
- Read `references/safety-rules.md` before exposing event metadata in any UI.
- Copy/adapt `assets/react/ProductLensPanel.tsx` for React products. It is a headless-style template; map its class names to the host product's design system.
- Read `references/language-adapters.md` when integrating with JavaScript/TypeScript, Python, Java, or another backend stack.
- Start from `assets/product-lens-manifest.example.json`.
- Use `examples/explainit/product-lens.manifest.json` only as a case study. Do not copy its workflow names or stages unless the target product has the same domain.

## Language And Framework Scope

The Product Lens contract is language-agnostic: any product can emit safe workflow events with `workflowId`, `runId`, `stageId`, `status`, `at`, `summary`, and optional safe `meta`.

Bundled automation is intentionally lightweight:

- `scripts/scan_project.py` provides best-effort discovery for common JavaScript/TypeScript, Python, and Java web stacks.
- `assets/react/ProductLensPanel.tsx` is only a React UI scaffold. For Vue, Svelte, Angular, server-rendered templates, native mobile, desktop apps, or Java/Python-only products, implement the same manifest/event contract using the host UI framework.
- The skill does not provide full SDKs for every language. Prefer small local helpers that match the host codebase, such as `emitLensEvent(...)`, middleware, decorators, interceptors, or logging hooks.
- If the scanner misses a framework, continue manually from route handlers, controllers, services, jobs, queues, and existing telemetry boundaries.

## Product Lens Contract

The Lens must be removable. The original feature should keep working if all Lens UI and event listeners are disabled.

Use this contract:

- `manifest`: product-level workflow registry.
- `workflow`: one core product capability inside the manifest, identified by a stable `id`.
- `events`: runtime facts emitted by the product for one workflow run.
- `Lens UI`: separate observer surface that combines the manifest, workflow selection, and events.

Manifest workflows should include:

- `id`: stable lowercase identifier such as `checkout`, `document-import`, or `ai-generation`.
- `label`: user-facing workflow name.
- `description`: concise explanation of the workflow's user value.
- `entrypoints`: optional routes, buttons, commands, or jobs that start the workflow.
- `stages`: ordered stage list.
- `events`: expected event catalog for that workflow.

Events should include:

- `workflowId`: stable id from `manifest.workflows[]`.
- `runId`: stable id for one user action, request, job, or replay.
- `stageId`: stable id from the manifest.
- `status`: `waiting`, `running`, `success`, `warning`, or `error`.
- `at`: timestamp.
- `summary`: safe plain-language summary.
- `meta`: optional safe counts, durations, provider labels, retry state, cache state, or redacted ids.

Prefer this runtime shape:

```ts
interface LensEvent {
  workflowId: string;
  runId: string;
  stageId: string;
  status: 'waiting' | 'running' | 'success' | 'warning' | 'error';
  at: string;
  summary: string;
  meta?: Record<string, string | number | boolean>;
}
```

## Instrumentation Rules

- Prefer existing lifecycle boundaries: form submit, route handler start, cache hit, model call start/end, queue job start/end, SSE event, webhook event, render completion.
- Keep instrumentation append-only and removable. Do not change business behavior to support Lens.
- Emit `workflowId`, `runId`, timestamps, and stage ids. Avoid full payloads.
- Use safe metadata such as item counts, durations, provider names, retry state, cache hit/miss, or redacted labels.
- For AI products, show model-call phases and output categories, not raw prompts, system messages, API keys, or private user text.
- For production, prefer live events or replayed trace events over a static full blueprint. Static manifest-only mode is acceptable only for planning, docs, or demos without a running app.
- For products with multiple core features, keep workflow event streams isolated. A checkout run should never update an import workflow timeline, and a background job should never overwrite a foreground request run.

## UI Rules

Use one of these surfaces:

- Dedicated route: `/lens`, `/how-it-works`, `/trace`, or `/workflow`.
- Sidecar drawer that opens beside the product without covering the primary task.
- Separate internal/dev companion page.
- Replay viewer for a saved trace.

Match the host product:

- Reuse the existing app shell, route layout, navigation pattern, typography, spacing, icons, buttons, form controls, empty states, loading states, and color tokens.
- Prefer the host product's component library, such as its existing `Button`, `Select`, `Card`, `Tabs`, `Badge`, `Timeline`, or page layout components.
- If no design system exists, use low-specificity semantic classes or CSS variables so the product can style the Lens later.
- Keep the bundled React component visually neutral. Treat it as structure and accessibility scaffolding, not a finished brand style.

The UI should show:

- Current workflow name and run status.
- Workflow selector when more than one workflow exists.
- Run selector or replay control when multiple runs are available.
- Ordered stage timeline.
- Stage owner and safe explanation.
- Incremental event arrival, with timestamps or elapsed time.
- Degraded/error states that explain what stayed usable.
- Short safety note that the Lens exposes summaries only.

Avoid:

- Embedding the Lens directly inside the core business result.
- Shipping a Lens page with a separate visual brand, fixed palette, fixed typography, or sample-project styling.
- Copying the style of an example project into another product.
- Showing all stages as complete before a request actually runs.
- Displaying secrets, prompts, tokens, full bodies, or personal data.
- Turning implementation trivia into user-facing noise.

## Exposure Rules

Product Lens is often most useful in development, testing, demos, onboarding, and internal review. Do not expose it in production by accident.

- Add a product-owned switch such as `PRODUCT_LENS_ENABLED`, `NEXT_PUBLIC_PRODUCT_LENS_ENABLED`, `VITE_PRODUCT_LENS_ENABLED`, or a server-side feature flag.
- Default the switch to disabled for production.
- Gate the Lens route, navigation entry, floating shortcut, event capture, replay storage, and trace endpoints with the same switch or equivalent access control.
- If the Lens must be available in production, protect it with an internal role, admin permission, signed demo link, or explicit public transparency requirement.
- When disabled, the original product must keep working and the Lens route should return 404, redirect, or hide itself according to the host product's routing convention.

## Validation Checklist

- The original feature works with Lens disabled.
- A feature flag or access-control switch can disable Lens UI, routes, trace endpoints, and shortcuts.
- Production defaults do not expose the Lens unless explicitly configured.
- The Lens lives on a separate surface unless inline mode was explicitly requested.
- The Lens page follows the host product's UI/UX system rather than a sample-project style.
- Each declared workflow has a stable id, stages, and event catalog.
- Runtime events include `workflowId`, `runId`, `stageId`, `status`, `at`, and `summary`.
- At least one real run lights up stages sequentially for every instrumented workflow.
- Multiple workflows do not leak events into each other.
- Empty, running, success, degraded, and error states are understandable.
- Manifest validation passes.
- No API keys, raw prompts, auth tokens, environment values, full request bodies, or personal data are exposed.
- A non-technical viewer can explain the workflow after watching the Lens for 30 seconds.

## Genericity Rules

- Do not design the Lens as a companion feature for only the current product unless the user explicitly asks for a one-off implementation.
- Do not hardcode workflow ids, stages, event names, or UI labels from a sample project into the skill's reusable rules.
- Treat examples as validation cases, not as the default product model.
- When a product has a legacy flow and a new flow, model them as two independent workflows under the same manifest instead of forking the Lens implementation.
