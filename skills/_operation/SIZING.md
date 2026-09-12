<!-- operation:contract -->
# SIZING — how much process the situation is worth

Operations is where over-process and under-process both kill people's evenings.
A readiness review applied to an internal dashboard blocks it needlessly; the
same review skipped on a payment path ships the outage. **The scale is read off
the subject, not off the request.**

## Two scales, and they are not the same

| Scale | Answers | Set by | Lives in |
|---|---|---|---|
| **Service tier** `T0`-`T3` | How much this service failing costs | the service, once | `operation-readiness` |
| **Safety tier** `T1`-`T4` | How much *this action* can destroy | the action, every time | `_operation/SAFETY_TIERS.md` |

**Neither is a ceremony dial.** A `T3` service still gets a real rollback plan;
a `T4` action still requires its approver at 3 a.m. What scales is the depth of
the review and the number of people involved, never the observation rung or the
approval the tier demands.

## Match the depth to the subject

- **Assign the service tier before applying any requirement.** A review that
  applies one bar to everything is either blocking the dashboard or waving the
  payment path through, and both look like diligence
- **Classify the action's safety tier before designing the steps.** The tier
  decides whether a procedure needs approvals, a two-person rule, or must not be
  automated at all
- **State the checks you deliberately skipped.** A silent skip reads as coverage
  that was never there — which, in this domain, is discovered during an incident

## Incident pressure changes the approver, never the tier

This is the rule the rest of the file exists for. Under an outage everyone finds
reasons that the usual bar does not apply. **The safety tier of an action is a
property of the action**: a database drop is `T4` at 14:00 and `T4` at 03:00.
What an incident may change is who is available to approve it and how fast the
approval happens — and that substitution is recorded, not assumed.

## When a dialogue is required first

Before executing, any of these makes the dialogue mandatory:

- The shape of the deliverable is not uniquely determined
- A **threshold** is implied but unstated — "acceptable error rate", "enough
  monitoring", "reasonable page load" are numbers somebody has to choose, and an
  agent choosing them silently has taken the decision
- The work would set a gate, a freeze, or an escalation path that binds other people
- The action is `T3` or above and its approver is not identified
- A term in the request, the runbook, the alert or the design carries two
  meanings, or one concept goes by two names, and the host's glossary does not
  settle it

**Reading to find out is not executing.** The dashboards, the incident history,
the existing runbooks and the current rota answer more than the person can. And
never open a dialogue over one `T1` action with an obvious procedure.

## Terms — one name per concept, one concept per name

The host's glossary is `.agents/glossary.md` when it exists. Read it before the
work is sized and write with its names only — runbook, record, report alike. A
term the work has to coin goes into the handoff's `terms`, and on anything
beyond a one-action `T1` it is proposed in the dialogue rather than invented on
the way.

**An ambiguous or inconsistent term is never resolved by a silent choice.**
Two meanings for one word, or two names for one concept, is a question
(`_operation/REPORT.md`): one question, with the default named — the spelling
the runbooks and dashboards already use most. The answer lands in `terms` and is
appended to the glossary as `term · means · not to be called`, so the next run
inherits the decision rather than the ambiguity. A run that opened a dialogue
may create the glossary for its first settled term; a one-action `T1` run never
does — it marks what it found `OUT-OF-SCOPE` and moves on. Two concepts keep
two names: a `handover` passes a service to a team, a handoff passes work
between skills, and neither is renamed to match the other.
