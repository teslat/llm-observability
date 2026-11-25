# LLM observability report: sample-app

_Scope: `examples/sample-app` · Method: decisions-first, 3-tier model · Produced by following the `llm-observability` skill_

## Summary

The app calls an LLM from 5 places in 4 files: two Python SDKs, openai-php in Laravel, and the Vercel AI SDK. Nothing is instrumented, and every call site talks to its SDK directly, so there is no single place to add tracing yet. The biggest risks are a silent fallback in `summarize.py`, which hides failures, and full invoice text plus customer emails written to logs. Do this first: route each language through one traced wrapper (Phase 0) and stop logging raw invoice content.

## Call sites

| # | File:line | Provider / SDK | Feature | Tenant source | Prompt version | Tags present | Fallback? | PII risk |
|---|---|---|---|---|---|---|---|---|
| 1 | `src/summarize.py:11` | openai (Python) | invoice_summary | none (no tenant in scope) | none, inline string | none | **yes**, to a cheaper model on any exception | **high**: invoice text and customer email logged at INFO |
| 2 | `src/summarize.py:17` | openai (Python) | invoice_summary (fallback) | none | none | none | is the fallback | same as #1 |
| 3 | `src/support.py:9` | anthropic (Python) | support_reply | `tenant_id` argument | `SUPPORT_PROMPT_V3` (version is in the variable name only) | none | no | low: tenant name in the system prompt |
| 4 | `app/Services/InvoiceAssistant.php:11` | openai-php (Laravel) | invoice_explain | `$tenantId` argument | none | none | no | medium: user question sent as-is |
| 5 | `web/chat.ts:5` | Vercel AI SDK | reply_draft | none | none, inline template | none | no | medium: ticket text sent as-is |

Removed as false positives: `src/inbox.py:8` (`self.messages.create`) is a mailbox store, not an LLM call. The scanner already skips it because the file imports no LLM library.

## Checklist score

**Foundation (Phase 0)**
- ❌ Every LLM call is a span with GenAI attributes: no OpenTelemetry in any file.
- ❌ Feature, tenant, prompt version, response model on every span: none tagged. A tenant ID is available at #3 and #4 but isn't recorded.
- ❌ PII redacted before storage: `summarize.py:9` logs invoice text and a customer email.
- ❌ Trace IDs linked to business events: no invoice or ticket ID is attached.

**Tier 1: Alerts**
- ❌ No alerts defined.
- ❌ Fallbacks are counted as failures: `summarize.py:15` catches every exception and retries on a cheaper model, with no record that it happened.

**Tier 2, Quality, Cost and governance:** ❓ These are team practices the code can't show. See the open questions below.

**Portability**
- ⚠️ No vendor observability SDK, which makes Phase 0 easy, but also no OpenTelemetry yet.

## Recommendations by phase

### Phase 0: Foundation
- Add `TracedLlm` wrappers: Python in `src/llm.py`, PHP in `app/Services/TracedLlm.php`, TS in `web/llm.ts`. Route all 5 call sites through them (templates in `references/`). **Job:** every later signal depends on these tags.
- Tag every span with `app.feature`, `app.tenant_id` (where it exists), `app.prompt_version` and `gen_ai.response.model`. **Job:** investigation, plus breaking down Tier 1 and Tier 2 by feature and tenant.
- Replace `log.info(... customer_email, invoice_text)` in `summarize.py:9` with an invoice ID only. **Job:** governance; this removes the PII risk.
- Name prompt versions explicitly, e.g. `support_reply@v3` instead of a variable suffix.

### Phase 1: Reliability and cost
- Record the fallback in `summarize.py`: set `app.fallback_used=true` and `app.outcome="fallback"` on the span, and catch specific provider errors instead of every exception. **Job:** Tier 1 alert on the error+fallback rate.
- Record token usage on every span to get cost per feature and per tenant. **Job:** weekly review and budget burn.

### Phase 2: Quality
- Build a golden set for `invoice_summary` from real invoices (50 to 200, with PII removed) and gate prompt changes in CI.

### Phase 3: Feedback loop
- If the UI lets users edit `reply_draft` output, log the edit as an event on the same trace. Edits become eval cases.

### Phase 4: Safety and governance
- Agree on retention for prompt content (for example 7 days raw, 13 months aggregates) before turning on any content capture.

## Proposed Tier 1 alerts

| Signal | SLO / threshold | Window | Owner | Runbook | First action |
|---|---|---|---|---|---|
| p95 latency (feature: invoice_summary) | p95 < ____ s | ____ min | ____ | link | Check provider health, then recent prompt or model changes |
| Error + fallback rate (all features) | < ____ % | ____ min | ____ | link | Split by provider, model and prompt version |
| Budget burn | < ____ % of budget by ____ | daily | ____ | link | Find the feature or tenant driving spend |

The thresholds are blank on purpose. Run for about two weeks with Phase 0 tags in place, then set each one from the observed baseline. The guardrail alert waits until guardrails exist.

## Signals to drop

None yet; nothing is collected. The one thing to remove is the INFO log of raw invoice text: it does none of the three jobs and creates a PII risk.

## Open questions for the team

- Is `invoice_summary` multi-tenant? It has no tenant in scope.
- Who owns each proposed alert, and what are the monthly budgets per feature?
- Which OpenTelemetry backend will you use (self-hosted Langfuse, Grafana, other)? Only the exporter config depends on it.
