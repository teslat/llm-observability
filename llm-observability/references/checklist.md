# Scoring checklist

Mark each item ✅ (done), ⚠️ (partial) or ❌ (missing), with the evidence (file:line) or the reason.

## Foundation (Phase 0)
- Every LLM call is a span with OpenTelemetry GenAI attributes
- Every span has feature, tenant ID, prompt version and response model
- PII is redacted before anything is stored
- Trace IDs are linked to business events

## Tier 1: Alerts
- 3 to 5 alerts, no more
- Each has an SLO, one owner and a runbook
- Fallbacks are counted as failures

## Tier 2: Weekly review
- Cost per feature and per tenant
- Cost per successful outcome
- Eval score trend, regeneration and edit rates, model mix
- A fixed day and a named reviewer

## Quality
- Golden dataset of 50 to 200 real cases
- Eval gate in CI
- Sampled LLM-as-judge on live traffic
- Regenerations and edits become new eval cases

## Cost and governance
- 100% of errors and about 5 to 10% of successes sampled
- Tiered retention (for example 7 days raw, 13 months aggregates)
- Observability spend tracked as a share of LLM spend
- Guardrail audit trail and retention policy agreed

## Portability
- Code emits OpenTelemetry; the backend can be swapped by configuration

Most items under Tier 2, Quality and governance are team practices, not code. Mark them ❓ (unknown from the code) unless the repo shows evidence, and ask the user.
