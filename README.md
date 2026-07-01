# Product Lens Skill

Product Lens is a Codex skill for adding a standalone, live workflow explainer to an existing product.

It helps you show how a product feature works step by step without rewriting the product's core logic or embedding explanation UI into the primary business surface.

## What It Creates

- A workflow manifest that names stages, owners, safe inputs, safe outputs, and risks.
- Lightweight instrumentation around existing lifecycle events.
- A separate Lens page, drawer, route, or companion app.
- A live or replayable timeline that lights up as a real request runs.
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
Use $product-lens to add a standalone /lens page for the main request flow in this product.
```

## Quick Start

1. Scan your project:

```bash
python scripts/scan_project.py /path/to/project --json
```

2. Draft a manifest from `assets/product-lens-manifest.example.json`.

3. Validate it:

```bash
python scripts/validate_manifest.py product-lens.manifest.json
```

4. Add safe events around existing boundaries such as submit, route start, model call start, model call end, render, save, and error.

5. Render those events in a separate `/lens`, `/trace`, `/how-it-works`, drawer, or companion page.

## Principle

Product Lens is a sidecar. The original product must keep working if the Lens is removed.

Static manifests are useful for planning, but the final product should show real live events or a replayed trace one step at a time.

## Project Layout

```text
SKILL.md
agents/openai.yaml
scripts/scan_project.py
scripts/validate_manifest.py
references/integration-patterns.md
references/safety-rules.md
assets/product-lens-manifest.example.json
assets/react/ProductLensPanel.tsx
examples/explainit/product-lens.manifest.json
examples/explainit/events.sample.json
```

## License

MIT
