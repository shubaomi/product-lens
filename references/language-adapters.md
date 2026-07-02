# Product Lens Language Adapters

Use the same manifest and runtime event contract in every language. Keep adapters local, small, and shaped like the host codebase.

## Universal Event Contract

Every emitted event should contain:

- `workflowId`: stable workflow id from `manifest.workflows[]`.
- `runId`: one user action, request, job, or replay.
- `stageId`: stage id inside that workflow.
- `status`: `waiting`, `running`, `success`, `warning`, or `error`.
- `at`: ISO timestamp.
- `summary`: safe plain-language summary.
- `meta`: optional safe counts, durations, provider labels, cache state, retry state, or redacted ids.

## JavaScript And TypeScript

Good fit: React, Vue, Svelte, Next.js, Remix, Express, Fastify, NestJS, Vite apps.

Typical boundaries:

- Form submit or command start.
- Route handler start/end.
- Cache lookup.
- Model/API call start/end.
- Stream chunk milestones.
- Render, save, error, and completion.

Prefer a local helper such as:

```ts
emitLensEvent(workflowId, runId, stageId, status, summary, meta);
```

For React products, adapt `assets/react/ProductLensPanel.tsx`. For non-React products, keep the same state model and rebuild the UI using the host framework.

## Python

Good fit: FastAPI, Flask, Django, Celery/RQ workers, notebook-backed tools.

Typical boundaries:

- FastAPI/Flask route start and response.
- Django view/service boundary.
- Background task queue start/end.
- StreamingResponse or generator yield milestones.
- Database, search, model, or third-party API calls.

Prefer a local helper such as:

```py
emit_lens_event(workflow_id, run_id, stage_id, status, summary, meta=None)
```

Send events through the product's existing mechanism: SSE, WebSocket, polling endpoint, logs, in-memory trace store, Redis, or database-backed trace table.

## Java

Good fit: Spring Boot, Spring MVC/WebFlux, Quarkus, Micronaut, background jobs, batch workers.

Typical boundaries:

- Controller method start/end.
- Service method start/end.
- WebClient/RestTemplate/model provider calls.
- Spring events, interceptors, filters, or AOP aspects.
- Async job start/end and error handling.

Prefer a local helper such as:

```java
lensEvents.emit(workflowId, runId, stageId, status, summary, meta);
```

For Spring, keep instrumentation close to controllers/services first. Use filters, interceptors, or aspects only when they match the product's existing patterns.

## Unsupported Or Unrecognized Stacks

If `scan_project.py` misses the stack, do not force a JavaScript-shaped solution. Identify:

1. The user action that starts each workflow.
2. The server/controller/job boundary.
3. The core business operation.
4. External calls or AI/model operations.
5. Persistence, rendering, notification, or completion.
6. Failure/degraded states.

Then emit the universal event contract from those boundaries and render the Lens in the host UI system.
