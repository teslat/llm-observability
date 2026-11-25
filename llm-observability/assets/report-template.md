# LLM observability report: <project name>

_Date: <date> · Scope: <paths scanned> · Method: decisions-first, 3-tier model_

## Summary

<3 to 5 sentences: how many LLM call sites, whether they share a wrapper, the biggest gap, and the one thing to do first.>

## Call sites

| # | File:line | Provider / SDK | Feature | Tenant source | Prompt version | Tags present | Fallback? | PII risk |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |

<Note false positives you removed and anything the scanner couldn't see (gateways, raw HTTP, workers).>

## Checklist score

<Copy references/checklist.md sections with ✅ ⚠️ ❌ ❓ and evidence.>

## Recommendations by phase

### Phase 0: Foundation
- <Concrete change, with file paths.> **Job:** <which of the 3 jobs it enables>

### Phase 1: Reliability and cost
### Phase 2: Quality
### Phase 3: Feedback loop
### Phase 4: Safety and governance

## Proposed Tier 1 alerts (3 to 5)

<Table from references/slo-template.md. Blanks where there's no baseline yet, plus how to measure it.>

## Signals to drop

<Anything currently collected that does none of the 3 jobs, with the reason.>

## Open questions for the team

<What the code can't answer: owners, budgets, retention rules, multi-tenancy.>
