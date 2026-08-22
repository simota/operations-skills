<!-- operation:deferred -->
# Postmortem

Purpose: Blameless narrative, contributing factors, counterfactual discipline, typed action items.
Read when: blameless narrative, contributing factors, counterfactual discipline, typed action items
Verified: 2026-08-21 — no automated check.

## Blameless Discipline

Blameless does not mean consequence-free. It means: **the object of analysis is the system,
not the person.** People act rationally given the information and pressures they had. If a
person could cause this outage, the system permitted it — that is the finding.

| Blaming | Blameless |
|---------|-----------|
| "X deployed without testing" | "The pipeline permitted a deploy with no integration gate" |
| "The on-call missed the alert" | "The alert routed to a channel with no paging integration" |
| "Y ran the wrong command" | "The production and staging commands differ by one character, with no confirmation" |
| "The team should have known" | "The knowledge existed only in one person's memory; no runbook covered it" |

**The rewrite test:** if a finding names a person, or would embarrass one, rewrite it as a
property of the system. If it cannot be rewritten, it is not a finding.

## The Counterfactual Trap

Counterfactuals — "if only they had checked the dashboard" — feel like findings and are not.
They describe a world that did not happen and give no actionable change.

| Counterfactual (reject) | Finding (accept) |
|-------------------------|------------------|
| "They should have noticed the memory graph" | "The memory graph is on a dashboard nobody opens during an incident; no alert existed" |
| "The rollback should have been faster" | "Rollback required manual approval from a person who was asleep" |
| "Better testing would have caught it" | "The test suite has no case covering an empty upstream response" |

Run the counterfactual check on every finding before admitting it. Any finding containing
"should have", "could have", or "failed to" is rewritten or dropped.

## Structure

```markdown
# Postmortem: <title — impact in user terms>
Date: <YYYY-MM-DD>  |  Severity: SEV<n>  |  Duration: <mitigation time> / <resolution time>
Authors: <names>  |  Status: draft | in review | final

## Summary
<3-5 sentences. Impact, cause, resolution. Readable by someone with no context.>

## Impact
<The impact statement from reference/impact-assessment.md. Quantified. User terms.>
| Dimension | Impact |
| Users | |
| Duration | |
| Data | |
| Financial | |
| Regulatory | |

## Timeline
All times UTC (<local offset stated once>).
| Time | Event | Evidence |
|------|-------|----------|
Include: first fault, first signal, detection, declaration, each decision, each mitigation
attempt (including failures), verification, all-clear.

## Detection
How was it found? By whom? How long from fault to signal (MTTD)?
Was there a signal that fired and was not acted on? Was there a signal that should have existed?

## Response
What went well. What was slow, and why. Where the response structure held or broke.

## Contributing Factors
<Not "the root cause". Complex systems fail through combinations.>
1. <Factor> — <how it contributed> — <observation rung>
2. ...
Each factor states its observation rung. Anything below O2 is labelled "hypothesis, unverified".

## What Went Well
<Genuine, specific. Not a courtesy section — these are the controls worth protecting.>

## Where We Got Lucky
<The most under-used section. What would have made this materially worse, and did not happen
by chance rather than by design? Each entry is a candidate action item.>

## Action Items
| # | Action | Type | Owner | Due | Priority | Tracking |

## Open Questions
<Unresolved, with who is chasing them.>
```

## Contributing Factors, Not Root Cause

Non-trivial outages have no single root cause. "5 Whys" run to a single answer produces a
convenient culprit and hides the other conditions. Enumerate factors across:

- **Trigger** — what started it
- **Latent condition** — what had been true and unnoticed, sometimes for months
- **Amplifier** — what made it bigger (retry storms, cascading timeouts, autoscaling)
- **Detection gap** — why it was not caught earlier
- **Response friction** — what made recovery slower than necessary

A postmortem with only a trigger is incomplete. The latent condition is usually where the
durable fix lives.

## Typed Action Items

Type every item — this is what stops a corpus of postmortems producing only "add more tests".

| Type | Reduces | Example |
|------|---------|---------|
| `PREVENT` | Probability | Add the integration gate to the pipeline |
| `DETECT` | MTTD | Alert on the SLI that was silent |
| `DIAGNOSE` | Time to understand | Add the missing dashboard or correlation ID |
| `MITIGATE` | MTTM | Write the runbook; add the feature flag |
| `RECOVER` | Data/state recovery time | Test and document the restore path |
| `PROCESS` | Response friction | Fix the escalation timeout |
| `LEARN` | Recurrence across teams | Share the failure mode; add to onboarding |

**A postmortem with only `PREVENT` items is a weak postmortem.** Prevention alone assumes you
can enumerate all future failures. `DETECT` and `MITIGATE` items pay off on failures nobody
predicted, and are usually cheaper.

### Action Item Rules

- Every item has a **named individual** owner. "The team" and "Platform" are not owners.
- Every item has a due date. No date means it will not happen.
- Every item is tracked in the normal work system, not only in the document.
- Items are scoped to be completable. "Improve reliability" is not an action item.
- Each item routes to the skill that owns the fix — `operation-runbook`, `operation-oncall`,
  `operation-change`, or `operation-readiness`.
- **Completion is reviewed.** An action-item completion rate below 70% at 90 days means the
  postmortem process is theatre; report the rate.

## Review

- SEV1: within 5 business days. SEV2: within 10.
- Review meeting includes responders **and** people who were not there — outsiders ask the
  questions insiders have normalised.
- The document is written before the meeting, not during it.
- Facilitator is not the IC. The IC is a witness, and needs to be able to be questioned.

## Pattern Review

Quarterly, across the postmortem corpus:

- Cluster by contributing factor, by component, and by detection gap.
- A factor appearing in ≥3 postmortems is a **systemic finding** — route it to
  `operation-readiness`, not to another per-incident action item.
- Track cumulative cost per cluster (total impact minutes, responder hours) — this is the
  argument that funds the durable fix.
- Track action-item completion rate. Falling completion predicts repeat incidents.
- Repeat incidents on the same component within 90 days: escalate to the service owner as a
  fitness question, not as another incident.
