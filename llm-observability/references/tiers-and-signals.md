# Tiers and signals

## The three tiers

| Tier | Purpose | What goes here | Rules |
|---|---|---|---|
| **Tier 1: Alerts** | Wake someone up | p95 latency, error and fallback rate, budget burn, guardrail spikes | 3 to 5 alerts maximum. Each has an SLO and one owner. |
| **Tier 2: Weekly review** | Change a decision | Cost per feature and per tenant, eval score trends, regeneration and edit rates, model mix | Reviewed on a fixed day by a named person. |
| **Tier 3: On demand** | Explain a failure | Full traces, prompt logs, agent step graphs | Sampled, not kept forever. Pulled when investigating. |

If you can't say which tier a signal belongs to, it probably belongs to none.

## The first 6 signals

| # | Signal | Tier | Why it matters |
|---|---|---|---|
| 1 | p95 latency per feature | 1 | Users feel the slow tail, not the average. |
| 2 | Error and fallback rate | 1 | A fallback hides a failure. Count it as one. |
| 3 | Budget burn (spend vs. daily or monthly budget) | 1 | LLM cost can grow faster than traffic. |
| 4 | Guardrail trigger rate (PII, jailbreak, policy) | 1 | A spike means an attack, a bug or a prompt change. |
| 5 | Cost per feature and per tenant | 2 | Shows which feature or customer pays for itself. |
| 6 | Eval score trend on a fixed dataset | 2 | Catches quality drift before users do. |

## Worth adding later

- Cost per successful outcome, not cost per call. A cheap call that fails is expensive.
- Retrieval quality for RAG: recall and chunk relevance.
- Provider and region health, so you know when the problem isn't yours.
- Trace IDs linked to business events (an order, a ticket, a claim), so a complaint leads straight to the trace.

## Rollout phases

- **Phase 0, foundation:** OpenTelemetry GenAI conventions; tag every call with trace_id, feature, tenant, prompt_version, model_version; redact PII before storage.
- **Phase 1, reliability and cost:** latency, errors, fallbacks, cost per feature/tenant, budget alerts.
- **Phase 2, quality:** golden dataset (50 to 200 real cases), eval gate in CI, sampled LLM-as-judge on live traffic.
- **Phase 3, feedback loop:** regenerations, edits and abandonment surface failures, which become eval cases, get fixed, then gated.
- **Phase 4, safety and governance:** guardrail metrics, jailbreak/PII audit trail, retention policies.

## Cost as policy

- Sample 100% of errors and about 5 to 10% of successes.
- Tiered retention, for example raw prompts 7 days, aggregates 13 months.
- Track observability spend as a share of LLM spend.

## No lock-in and ownership

- Emit OpenTelemetry; keep the backend swappable (self-hosted Langfuse, Grafana, any OTLP tool).
- Each Tier 1 signal has exactly one owner and one runbook.
