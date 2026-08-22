<!-- operation:guidance -->
# Glossary

Shared vocabulary across `operation-*` skills. Where an industry term has competing
definitions, the one below is authoritative for this repo.

## Time-to-X

| Term | Definition | Clock starts | Clock stops |
|------|------------|--------------|-------------|
| `MTTD` | Mean time to detect | Fault begins affecting users | Any signal fires (alert or report) |
| `MTTA` | Mean time to acknowledge | Page is sent | A human acknowledges |
| `MTTM` | Mean time to mitigate | **Impact begins** | User-visible impact ends |
| `MTTR` | Mean time to resolve | **Impact begins** | Underlying cause is fixed and verified |
| `MTTM(resp)` | Response-only mitigate | Page is sent | User-visible impact ends |

`MTTM` — not `MTTR` — is the number that matters to users. Track both; report `MTTM` to
stakeholders and `MTTR` to engineering.

**Start the user-facing clocks at impact, not at the page.** Measuring from the page silently
excludes detection time, so a service that takes 40 minutes to notice an outage and 5 to fix it
reports a 5-minute MTTM. Keep the response-only variant if the team wants to separate detection
from response quality — but label it, and never report it as MTTM.

## Roles

| Role | Owns | Never does |
|------|------|------------|
| `IC` (Incident Commander) | Decisions, priority, delegation | Hands-on debugging |
| `OL` (Operations Lead) | Executing mitigations | Deciding scope or severity |
| `CL` (Communications Lead) | Stakeholder + customer updates | Technical judgement calls |
| `Scribe` | Timeline capture in real time | Anything else |
| `Primary` / `Secondary` | On-call rotation positions | — |

## Change Classes

| Class | Definition | Approval |
|-------|------------|----------|
| `Standard` | Pre-approved, runbooked, previously executed unchanged | None — logged only |
| `Normal` | New or modified change with lead time | Service owner |
| `Emergency` | Required to restore or protect service now | IC, reviewed after the fact |

## Other

- **Toil** — manual, repetitive, automatable, tactical, devoid of enduring value, and
  scaling linearly with service size. All six must hold; work missing any one is not toil.
- **Day-2** — everything after the first successful production deploy.
- **Error budget** — the permitted unreliability, `1 − SLO` applied to the SLI's own unit over
  the window. For a **request-based** SLO it is a count of failed events
  (`(1 − SLO) × total valid events`); for a **time-based** availability SLO it is a duration
  (`(1 − SLO) × window`). Using the time form on a request-based SLO misstates the budget
  whenever traffic is not flat, which is always. Consumed, not earned back early.
- **DORA four keys** — deployment frequency, lead time for change, change failure rate,
  failed deployment recovery time.
- **Freeze** — a window in which `Normal` changes are refused. `Emergency` changes are
  never frozen; a freeze that blocks incident response is misconfigured.

## Output language

Prose follows the CLI global config. These stay in English regardless: code,
identifiers, file paths, CLI commands, metric names, alert names, severity
labels, YAML keys in emitted blocks, and the section headings of any document
this set generates.

