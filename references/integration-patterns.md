# Product Lens Integration Patterns

Use these patterns to add Product Lens without changing core business behavior.

## Product-Level Workflow Registry

Start every integration by listing the product's core workflows. Many products have several first-class flows, such as checkout, onboarding, import, generation, approval, reporting, and billing. Model each one as a separate `workflows[]` entry in the manifest.

Every runtime event must carry:

- `workflowId`: which workflow this run belongs to.
- `runId`: one user action, request, background job, or replay.
- `stageId`: a stage inside that workflow.
- `status`: `waiting`, `running`, `success`, `warning`, or `error`.
- `at`: timestamp.
- `summary`: safe plain-language summary.

Keep event stores keyed by both `workflowId` and `runId`. Do not let events from one workflow update another workflow's timeline.

## Host UI Adaptation

Product Lens should look like part of the host product, not like a separate branded plugin.

1. Inspect the host product's page shell, navigation, spacing, typography, color tokens, buttons, selects, tabs, cards, badges, timeline components, loading states, and empty states.
2. Reuse existing components and design tokens before introducing any new CSS.
3. If copying `assets/react/ProductLensPanel.tsx`, map its semantic classes through `classNames` or style `.product-lens__*` selectors in the host product.
4. Keep Lens copy and controls consistent with the host product's language, density, and interaction model.
5. Avoid fixed sample colors, fonts, shadows, rounded corners, or page composition.

## Pattern A: Existing Stream Or SSE Events

Use when a product already streams progress or partial results.

1. Keep the existing stream contract intact.
2. Add safe `status` or `trace` events between existing data events.
3. Include `workflowId` and `runId` on every Lens event.
4. Map each event name to a manifest stage inside the matching workflow.
5. Render events on a separate Lens page or drawer.
6. Store only safe summaries for replay.

Good fit: AI apps, long-running generation, import/export jobs, ETL progress, onboarding flows.

## Pattern B: Route Handler Milestones

Use when one API route coordinates a workflow.

1. Add a small local `emitLensEvent(workflowId, runId, stageId, status, summary, meta)` helper.
2. Emit before/after validation, cache lookup, model call, database write, and response send.
3. Never emit request bodies, headers, tokens, or raw provider payloads.
4. Send events through SSE, WebSocket, polling, logs, or an in-memory trace store.

Good fit: Express, Fastify, Next.js route handlers, Rails controllers, Django views.

## Pattern C: Frontend State Machine

Use when most of the workflow is visible in UI state.

1. Identify existing states such as `idle`, `submitting`, `streaming`, `rendering`, `saved`, `error`.
2. Map state transitions to manifest stages for the active workflow.
3. Show safe local-only metadata.
4. Keep Lens UI separate from the core result.

Good fit: client-heavy products, dashboards, design tools, internal workflows.

## Pattern D: Background Job Trace

Use when a user action starts asynchronous work.

1. Attach a trace id to the job.
2. Attach the job to a `workflowId`.
3. Emit stage events from queue start, worker start, external calls, persistence, and completion.
4. Surface status through a dedicated trace endpoint.
5. Render live progress and allow replay after completion.

Good fit: imports, exports, video processing, document parsing, billing workflows.

## Pattern E: Manifest-Only Planning

Use only when no running product is available yet.

1. Build a static manifest from product knowledge.
2. Mark the Lens as planning/demo mode.
3. Do not imply stages are live.
4. Upgrade to real events before presenting it as a working Product Lens.

## Pattern F: Legacy And New Flow Coexistence

Use when a product keeps an existing workflow while adding a redesigned or expanded workflow.

1. Keep the old and new product flows independent.
2. Model each flow as a separate workflow in one product-level manifest.
3. Reuse the same Lens event contract and UI renderer.
4. Give each flow its own stage ids and event catalog.
5. Verify the old flow works without the new flow and the new flow works without the old flow.

Good fit: product redesigns, feature migrations, A/B variants, admin/user mode splits, and hackathon upgrades that preserve a stable baseline.

## Pattern G: Feature Flag And Access Control

Use when Lens is valuable for development, testing, demos, or internal education but should not be visible to every production user.

1. Add a product-owned switch such as `PRODUCT_LENS_ENABLED`, `NEXT_PUBLIC_PRODUCT_LENS_ENABLED`, `VITE_PRODUCT_LENS_ENABLED`, or an existing feature flag.
2. Default the switch to disabled in production.
3. Gate the Lens route, navigation entry, floating shortcut, trace endpoint, replay storage, and event capture.
4. If production access is required, combine the flag with an internal role, admin permission, signed demo link, or explicit public transparency mode.
5. Verify the product's normal workflows still run when the flag is disabled.

Good fit: SaaS products, internal tools, AI products with private prompts, regulated workflows, staged launches, and hackathon demos that later become production apps.
