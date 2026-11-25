---
name: llm-observability
description: Audit and instrument LLM features in a codebase using a decisions-first observability model (3 tiers, OpenTelemetry GenAI conventions, per-feature and per-tenant tagging, SLO templates). Use this whenever the user wants to add monitoring, tracing, logging, cost tracking, evals or alerts to code that calls an LLM (OpenAI, Anthropic, Gemini, Bedrock, LiteLLM, LangChain, Vercel AI SDK, openai-php, Prism), asks why their AI feature is slow, expensive or flaky in production, wants an "LLMOps" or "AI observability" review, or asks what to measure for an AI app, even if they don't say "observability".
license: MIT. See LICENSE in the repository root.
---

# LLM Observability

Help the user see what their LLM features are doing in production, without drowning them in data.

The core idea: **start from decisions, not metrics.** Every signal must do at least one job:
1. trigger an alert someone acts on,
2. feed a weekly review that changes a decision, or
3. help an investigation when something breaks.

A signal that does none of these costs money to store and attention to ignore. Recommend dropping it. This principle is the filter for every recommendation you make, so say which job each proposed signal does.

## Workflow

Work through these steps in order. Steps 1 to 3 are read-only. Don't change code until the user has seen the gap report, unless they asked you to instrument directly.

### 1. Find every LLM call site

Run the scanner from the repository root:

```bash
python3 <skill-dir>/scripts/find_llm_calls.py . --format md
```

It lists call sites for common SDKs in Python, PHP and JS/TS, and flags whether each file already has OpenTelemetry and which recommended tags are present. It's a heuristic:
- Open each hit and drop false positives (a method that happens to be named `create`, a test mock).
- Look for what it can't see: an internal gateway or proxy service, raw HTTP clients built in another module, queue workers that call the model. Search for the provider hostnames and for the project's own wrapper names.
- If the project already routes every call through one wrapper, that wrapper is the only place you need to instrument. Say so; it's the best news in the report.

### 2. Understand each call site

For each real call site, work out from the code:
- **feature**: what the user-facing feature is (e.g. `invoice_summary`, `support_reply`). Use the closest route, job or class name.
- **tenant**: where the tenant or customer ID comes from in that request, if the app is multi-tenant.
- **prompt version**: whether prompts are versioned at all. Unversioned prompts are a gap, because you can't tell which change caused a regression.
- **fallbacks and retries**: whether a failure silently falls back to another model or a canned answer. A fallback hides a failure, so it must be counted as one.
- **PII**: whether user content goes into logs or span attributes.

Ask the user only for what the code can't tell you (e.g. "is this app multi-tenant?").

### 3. Write the gap report

Fill `assets/report-template.md` and save it as `llm-observability-report.md` in the repo root (or where the user asks). Keep it short and concrete: file paths and line numbers, not general advice. Read `references/tiers-and-signals.md` for the tier model and the first 6 signals, and `references/checklist.md` to score the current state.

Order the recommendations by the rollout phases. A team that skips Phase 0 can't do the rest, because nothing can be broken down by feature, tenant or prompt version:
- **Phase 0, foundation:** OpenTelemetry GenAI conventions, tags on every call, PII redaction before storage.
- **Phase 1, reliability and cost:** latency, errors, fallbacks, cost per feature and tenant, budget alerts.
- **Phase 2, quality:** golden dataset (50 to 200 real cases), eval gate in CI, sampled LLM-as-judge.
- **Phase 3, feedback loop:** regenerations, edits and abandonment become eval cases.
- **Phase 4, safety and governance:** guardrail metrics, jailbreak/PII audit trail, retention.

### 4. Instrument (when the user agrees)

- **Instrument once, not everywhere.** Prefer one small wrapper per language that every call site goes through. Patching 30 call sites by hand drifts within a month.
- Use the templates in `references/instrumentation-python.md` or `references/instrumentation-laravel.md`. For JS/TS, follow the same pattern with `@opentelemetry/api` (`trace.getTracer(...)`, `tracer.startActiveSpan(...)`, `span.setAttributes(...)`, `span.recordException(...)`).
- Attach the attributes from `references/tagging-schema.json`. `gen_ai.*` names follow the OpenTelemetry GenAI semantic conventions; `app.*` names are the project's own.
- Emit OpenTelemetry from the code. Don't call a vendor SDK from business logic: the backend (self-hosted Langfuse, Grafana, any OTLP tool) should be swappable by configuration.
- **Never put raw prompts or responses in span attributes by default.** Redact PII first, and keep content capture opt-in and sampled. Logs and traces are often kept longer and seen by more people than the database.
- Match the project's existing style, dependency manager and OpenTelemetry version. If OpenTelemetry isn't set up at all, add the minimal SDK and exporter setup and say which environment variables it needs (`OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`).
- The GenAI conventions are still marked "Development". Older instrumentation libraries emit `gen_ai.system` where newer ones use `gen_ai.provider.name`. Check what the project's installed versions use and stay consistent; mention it in the report.

After editing, run the project's tests and linters if they exist. If you can't run them, say so.

### 5. Alerts, SLOs and cost policy

- Propose 3 to 5 Tier 1 alerts at most. Each needs an SLO, exactly one owner and a runbook. Use `references/slo-template.md`.
- **Never invent thresholds.** Thresholds come from the team's own baseline. Leave blanks (`____`) and explain how to measure the baseline, unless real numbers are in the repo or the user gives them.
- Cost as policy: keep 100% of errors and sample roughly 5 to 10% of successes; use tiered retention (for example raw prompts 7 days, aggregates 13 months); track observability spend as a share of LLM spend. Present these as starting points the team should adjust.

## What to hand back

1. `llm-observability-report.md` (the filled template).
2. If you instrumented: a short summary of files changed, the new wrapper, and the environment variables needed.
3. The single most useful next step, usually Phase 0 for the busiest feature.

Be honest about uncertainty: say which call sites you couldn't classify and which numbers are placeholders.

## Reference files

- `references/tiers-and-signals.md`: the 3 tiers, the first 6 signals, and signals worth adding later. Read before step 3.
- `references/tagging-schema.json`: attributes for every LLM span. Read before step 4.
- `references/instrumentation-python.md`, `references/instrumentation-laravel.md`: wrapper templates.
- `references/slo-template.md`: alert/SLO table and runbook minimum.
- `references/checklist.md`: scoring checklist for the report.
- `assets/report-template.md`: the report structure.
- `scripts/find_llm_calls.py`: call-site scanner (stdlib only, Python 3.8+).
