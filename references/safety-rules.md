# Product Lens Safety Rules

Product Lens is a trust feature. It should make a product more understandable without exposing private internals.

Default to private or disabled in production unless the product owner explicitly wants a public transparency surface.

## Never Display

- API keys, access tokens, session ids, refresh tokens, cookies, or credentials.
- Environment variables or secret configuration values.
- Raw system prompts, hidden instructions, complete model prompts, or chain-of-thought.
- Full request bodies, response bodies, headers, or provider payloads.
- Personal data, customer records, emails, phone numbers, payment details, addresses, or private documents.
- Internal vulnerability details, exploit strings, or security bypass steps.
- Workflow ids, run ids, source labels, or stage summaries that contain customer names, private project names, emails, phone numbers, or secret identifiers.
- Lens routes, trace endpoints, replay stores, or navigation entries that are accidentally exposed to public production users.

## Safe To Display

- Stage names and stage owners.
- Generic workflow ids such as `checkout`, `document-import`, or `ai-generation`.
- Timestamps, elapsed time, and coarse duration.
- Counts such as item count, token range, row count, card count, or retry count.
- Provider labels such as "AI provider", "database", or "search index".
- Cache hit/miss, retry state, degraded state, and error category.
- Redacted ids such as `run_...a7f2` or short hashes.
- User-facing concept labels when the product already shows them.

## AI Product Rules

- Explain model phases in plain language.
- Show output categories, not raw prompts.
- If a visual, audio, or structured layer fails, show the degraded path and what remains usable.
- Do not expose chain-of-thought. Use concise safe summaries instead.

## Redaction Checklist

Before shipping:

1. Search event producers for `key`, `token`, `secret`, `prompt`, `password`, `cookie`, `authorization`, `email`, and `phone`.
2. Confirm those fields are never emitted into Lens events.
3. Confirm `workflowId`, `runId`, and `stageId` values are generic or redacted.
4. Confirm production defaults disable or protect Lens UI, routes, trace endpoints, and replay data.
5. Validate sample manifests and sample events.
6. Watch one live run and one error run for each instrumented workflow.
7. Confirm a non-technical viewer can understand the workflow without seeing private payloads.
