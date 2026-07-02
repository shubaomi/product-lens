# Product Lens Skill

Product Lens is a Codex skill for adding standalone, live workflow explainers to an existing product.

It helps you show how one or many product workflows work step by step without rewriting the product's core logic or embedding explanation UI into the primary business surface.

## What It Creates

- A product-level workflow manifest that names workflows, stages, owners, safe inputs, safe outputs, and risks.
- Lightweight instrumentation around existing lifecycle events.
- A separate Lens page, drawer, route, or companion app that follows the host product's UI system.
- A live or replayable timeline that lights up as a real request runs.
- Workflow and run selection for products with multiple core capabilities.
- Feature flag or access-control guidance so Lens can stay private in production.
- Safety rules that prevent secrets, raw prompts, tokens, and private payloads from leaking.

## Typical Use Cases

- Explain an AI feature to non-technical users.
- Demo a hackathon product with a memorable transparency layer.
- Add onboarding for workflow-heavy SaaS features.
- Show internal request pipelines without exposing private internals.
- Package a reusable "how this product works" layer for open source adoption.

## Install

Copy this folder into a Codex skills directory, or reference it directly when asking Codex to use the skill.

Example prompt:

```text
Use $product-lens to add a standalone /lens page for the core workflows in this product.
```

## Quick Start

1. Scan your project:

```bash
python scripts/scan_project.py /path/to/project --json
```

2. Inspect the product's UI stack and choose the host components, route shell, tokens, and controls the Lens should reuse.

3. Add a product-owned switch such as:

```bash
PRODUCT_LENS_ENABLED=false
```

Use the product's existing config system when possible. Default the switch to disabled in production.

4. Draft a product-level manifest from `assets/product-lens-manifest.example.json`.

5. Validate it:

```bash
python scripts/validate_manifest.py product-lens.manifest.json
```

6. Add safe events around existing boundaries such as submit, route start, model call start, model call end, queue job start, render, save, and error.

```bash
python scripts/validate_events.py product-lens.manifest.json events.sample.json
```

7. Render those events in a separate `/lens`, `/trace`, `/how-it-works`, drawer, or companion page that reuses the host product's UI/UX.

## Principle

Product Lens is a sidecar. The original product must keep working if the Lens is removed.

Static manifests are useful for planning, but the final product should show real live events or a replayed trace one step at a time. When a product has multiple core workflows, keep them in one manifest and isolate events by `workflowId` and `runId`.

The bundled React panel is intentionally neutral. Treat it as structure and state handling, then map its `classNames` to the host product's components or CSS.

The manifest and event protocol are language-agnostic. The scanner has best-effort support for common JavaScript/TypeScript, Python, and Java web stacks, while the bundled UI template is React-only. For other languages or UI frameworks, implement the same event contract using the host product's normal patterns.

## Project Layout

```text
SKILL.md
agents/openai.yaml
scripts/scan_project.py
scripts/validate_manifest.py
scripts/validate_events.py
references/integration-patterns.md
references/language-adapters.md
references/safety-rules.md
assets/product-lens-manifest.example.json
assets/react/ProductLensPanel.tsx
examples/explainit/product-lens.manifest.json
examples/explainit/events.sample.json
```

## License

MIT
