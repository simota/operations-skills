<!-- operation:contract -->
# Observation Ladder

Operations runs on claims about a system nobody can see directly. Rank every claim, and
never let a lower rung masquerade as a higher one.

**The rungs are `O<n>`, and the letter is load-bearing.** This ladder grades *how directly
a claim was observed*, and `O1` is the strongest rung. Elsewhere in this ecosystem an
`E<n>` ladder grades something else — distance from the hypothesis that produced the code —
and it runs the other way, with `E0` weakest. Two ladders sharing one letter in one roster
is how a single `E1` comes to mean both "captured now" and "static analysis" on the same
page. **Never write `E<n>` for an observation rung**, and when a report crosses into a
verification claim, name which ladder each rung came from.

| Rung | Name | What it is | Usable for |
|------|------|------------|------------|
| `O1` | Observed | Metric, log line, trace, or command output captured now | Declaring, mitigating, closing |
| `O2` | Reproduced | The behaviour was triggered deliberately and repeated | Root cause claims |
| `O3` | Documented | Runbook, ADR, config in version control | Procedure design |
| `O4` | Reported | A human said so | Starting an investigation |
| `O5` | Inferred | Model reasoning with no artifact behind it | Hypothesis only |

## Rules

- **A root cause requires `O2`.** "The cache was probably cold" is `O5` — it is a
  hypothesis, and labelling it a cause closes the incident on a guess.
- **Mitigation may proceed on `O1`.** Stopping the bleeding does not wait for `O2`.
  Restore service first, prove cause second.
- **`O4` never survives a postmortem unchallenged.** Human recollection of timing is
  systematically wrong; reconcile every reported time against `O1` timestamps.
- **Cite the rung inline.** `payment-api 5xx rate 12% [O1: Grafana panel 44, 14:02 JST]`
  beats "payments are erroring".
- **State the gap when evidence is missing.** "No `O1` for the 13:40–13:55 window — the
  Collector was itself down" is a finding, not a blank.

## Timestamps

All operational timestamps are recorded in **UTC with the local offset stated once**, e.g.
`2026-08-21T05:02:11Z (14:02 JST)`. Mixed-zone timelines are the single most common cause
of a wrong postmortem sequence.

## Reporting shape

- **Lead with the operational answer**, then the evidence. During an incident, the first
  line is the current state of user impact — nothing else.
- **Tables for decisions, prose for reasoning.** A severity call, a tier, a go/no-go: table.
  Why: prose.
- **Every recommendation carries an observation rung** (`_operation/CONTRACT.md`) and, if it
  proposes an action, a `SAFETY_TIER` block (`_operation/SAFETY_TIERS.md`).
- **Name the gap.** Unknown is a valid output. Padding a checklist with `N/A` to look
  complete is a defect.
- **No invented telemetry.** Never state a metric value, alert name, dashboard, or runbook
  path that was not read from the repo, the tooling, or the user. If a value is needed and
  absent, say what to query and where.

## Status

| Status | Condition |
|---|---|
| `DONE` | Every claim carries a rung, every action a `SAFETY_TIER`, zero `UNVERIFIED` |
| `PARTIAL` | Everything else that produced work — a single `UNVERIFIED` lands here |
| `BLOCKED` | Could not proceed. Say what was tried and what stopped it |

**Falling short is reported as falling short.** During an incident this is the
rule that costs most to break: a mitigation reported as verified, and not, sends
everyone home while the impact continues.

## Residuals

Anything left behind is classified and appears in the handoff's `open` list.

| Class | Means |
|---|---|
| `BLOCKED` | Wanted, attempted, prevented |
| `OUT-OF-SCOPE` | Found during the work, outside what was agreed. Named, not fixed |
| `DEFERRED` | In scope, deliberately postponed, with the condition to resume named |
| `UNVERIFIED` | Claimed, with no `O1` or `O2` behind it — an untested rollback, an unexecuted runbook, a mitigation nobody watched take effect |

`UNVERIFIED` is the class this domain turns on. **An untested procedure and a
tested one are indistinguishable until the night you need it.**

A skill holding `Write` puts a `#TODO(agent): <class> — <action>` marker where a
reader would next look. The report closes and is gone; the marker stays.

## The completion sweep — never omitted

Before reporting, run both halves and state both results:

1. **Markers introduced by this run** — every one appears in `open` with a class
2. **Rungs** — every claim made, against every claim carrying a rung

Report it in one line: `swept, 1 marker / 1 in open; 14 claims / 14 runged`.
**While either pair fails to match, the status is not `DONE`.**

