# Product Lens Integration Patterns

Use these patterns to add Product Lens without changing core business behavior.

## Pattern A: Existing Stream Or SSE Events

Use when a product already streams progress or partial results.

1. Keep the existing stream contract intact.
2. Add safe `status` or `trace` events between existing data events.
3. Map each event name to a manifest stage.
4. Render events on a separate Lens page or drawer.
5. Store only safe summaries for replay.

Good fit: AI apps, long-running generation, import/export jobs, ETL progress, onboarding flows.

## Pattern B: Route Handler Milestones

Use when one API route coordinates a workflow.

1. Add a small local `emitLensEvent(stageId, status, summary, meta)` helper.
2. Emit before/after validation, cache lookup, model call, database write, and response send.
3. Never emit request bodies, headers, tokens, or raw provider payloads.
4. Send events through SSE, WebSocket, polling, logs, or an in-memory trace store.

Good fit: Express, Fastify, Next.js route handlers, Rails controllers, Django views.

## Pattern C: Frontend State Machine

Use when most of the workflow is visible in UI state.

1. Identify existing states such as `idle`, `submitting`, `streaming`, `rendering`, `saved`, `error`.
2. Map state transitions to manifest stages.
3. Show safe local-only metadata.
4. Keep Lens UI separate from the core result.

Good fit: client-heavy products, dashboards, design tools, internal workflows.

## Pattern D: Background Job Trace

Use when a user action starts asynchronous work.

1. Attach a trace id to the job.
2. Emit stage events from queue start, worker start, external calls, persistence, and completion.
3. Surface status through a dedicated trace endpoint.
4. Render live progress and allow replay after completion.

Good fit: imports, exports, video processing, document parsing, billing workflows.

## Pattern E: Manifest-Only Planning

Use only when no running product is available yet.

1. Build a static manifest from product knowledge.
2. Mark the Lens as planning/demo mode.
3. Do not imply stages are live.
4. Upgrade to real events before presenting it as a working Product Lens.
