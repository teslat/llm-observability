# Alert and SLO template

One row per Tier 1 signal, 3 to 5 rows at most. Set thresholds from the team's own baseline. Leave `____` where no baseline exists yet, and say how to measure it (for example: "run for 2 weeks with tagging, then set p95 at the observed p95 plus a margin the team agrees on").

| Signal | SLO / threshold | Window | Owner | Runbook | First action |
|---|---|---|---|---|---|
| p95 latency (feature: ____) | p95 < ____ s | ____ min | ____ | link | Check provider health, then recent prompt or model changes |
| Error + fallback rate | < ____ % | ____ min | ____ | link | Split by provider, model and prompt version |
| Budget burn | < ____ % of budget by ____ | daily | ____ | link | Find the feature or tenant driving spend |
| Guardrail spikes | < ____ per ____ | ____ min | ____ | link | Inspect sampled traces; check for a prompt release |

**Ownership rule:** every Tier 1 signal has exactly one owner and one runbook. An alert with no owner is noise. An alert with two owners has none.

## What a runbook needs, at minimum

- What the alert means, in one sentence.
- The first three things to check, in order.
- Which tags to filter by: feature, tenant, prompt version, model.
- When to roll back a prompt or model, and who can decide.
- Where the traces for this signal live (Tier 3).
