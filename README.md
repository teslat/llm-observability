# llm-observability: a Claude skill

**Audit and instrument the LLM features in your codebase, starting from decisions, not metrics.**

Give Claude this skill and ask something like *"add observability to our LLM calls"* or *"why can't we tell which AI feature is costing us money?"*. Claude will then:

1. **Find every LLM call site** in Python, PHP/Laravel and JS/TS. It covers OpenAI, Anthropic, Gemini, Bedrock, LiteLLM, LangChain, the Vercel AI SDK, openai-php, Prism and raw HTTP.
2. **Check each one** for tags (feature, tenant, prompt version, model), silent fallbacks and PII in logs.
3. **Write a gap report**, ordered by rollout phase, with file paths and line numbers.
4. **Add the instrumentation** with one OpenTelemetry wrapper per language, once you agree to it.
5. **Draft 3 to 5 Tier 1 alerts.** Each comes with an SLO, an owner and a runbook, and the thresholds are left for your own baseline, never invented.

See [`examples/sample-report.md`](examples/sample-report.md) for a real run against the deliberately un-instrumented app in [`examples/sample-app`](examples/sample-app).

## The model behind it

Every signal has to do one of three jobs:
- trigger an alert,
- feed a weekly review, or
- help an investigation.

If it does none of these, drop it.

| Tier | What | Rule |
|---|---|---|
| 1: Alerts | p95 latency, error + fallback rate, budget burn, guardrail spikes | 3 to 5 max, each with an SLO and one owner |
| 2: Weekly review | Cost per feature/tenant, eval trends, edits and regenerations, model mix | Fixed day, named reviewer |
| 3: On demand | Full traces, prompt logs, agent step graphs | Sampled, short retention |

The skill uses the OpenTelemetry GenAI semantic conventions, so the backend stays swappable (self-hosted Langfuse, Grafana, any OTLP tool).

## Install

**Claude Code: personal, all projects**
```bash
git clone https://github.com/teslat/llm-observability.git
mkdir -p ~/.claude/skills
cp -r llm-observability/llm-observability ~/.claude/skills/
```

**Claude Code: one project, shared with the team**
```bash
mkdir -p .claude/skills
cp -r llm-observability/llm-observability .claude/skills/
git add .claude/skills/llm-observability
```

**Claude app (claude.ai / desktop)**
1. Download `llm-observability.zip` from the [Releases](https://github.com/teslat/llm-observability/releases) page. The zip has the `llm-observability` folder at its root.
2. Go to **Customize → Skills → + → Create skill → Upload a skill** and select the zip. Code execution must be on.

## What's inside

```
llm-observability/
├── SKILL.md                         # workflow Claude follows
├── scripts/find_llm_calls.py        # call-site scanner (Python 3.8+, no dependencies)
├── references/
│   ├── tiers-and-signals.md         # 3 tiers, first 6 signals, rollout phases
│   ├── tagging-schema.json          # attributes for every LLM span
│   ├── instrumentation-python.md    # wrapper template
│   ├── instrumentation-laravel.md   # wrapper template
│   ├── slo-template.md              # alert/SLO table + runbook minimum
│   └── checklist.md                 # scoring checklist
└── assets/report-template.md        # report structure
```

You can also run the scanner on its own:
```bash
python3 llm-observability/scripts/find_llm_calls.py path/to/repo           # Markdown table
python3 llm-observability/scripts/find_llm_calls.py path/to/repo --format json
```

## Limits

- **Call-site detection is a heuristic.** It can miss calls made through an internal gateway or a wrapper with a custom name, and Claude is told to look for those. It can also flag unrelated methods, which Claude is told to drop.
- **The GenAI conventions are still marked Development.** Attribute names can change between OpenTelemetry versions, and the skill checks which ones your installed packages use.
- **Thresholds are left blank on purpose.** Set them from your own baseline.

## Companion: The AI Observability Playbook

This skill puts *The AI Observability Playbook* into practice: 10 pages covering the tiers, rollout phases, tagging schema, OpenTelemetry snippets, an SLO template and a checklist. Get it free from [my LinkedIn](https://www.linkedin.com/in/muhammadbermawy/).

---

By **Muhammad El Bermawy**, System Architect · *Systems Thinking for Builders*. MIT licensed. Issues and PRs are welcome.
