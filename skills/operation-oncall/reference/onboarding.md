<!-- operation:deferred -->
# On-call Onboarding

Purpose: Shadow rotations, on-call readiness checklist, first-solo-shift gating.
Read when: shadow rotations, on-call readiness checklist, first-solo-shift gating
Verified: 2026-08-21 — no automated check.

## Readiness Checklist

A responder is ready for an unsupervised shift when **all** are true. Time served is not on
this list; three months of tenure proves nothing about pager readiness.

### Access — verified by use, not by grant

- [ ] Paging tool installed, notifications tested end-to-end, override-do-not-disturb confirmed
- [ ] Production read access, exercised at least once
- [ ] Dashboards and log tooling, exercised at least once
- [ ] Deploy/rollback permission for the services in scope, exercised in a non-prod environment
- [ ] Incident tooling: war-room creation, status page, comms templates
- [ ] Escalation contacts reachable and stored offline (a phone list that survives an outage
      of the tool holding the phone list)

### Knowledge

- [ ] Can name the service's SLOs and the current error budget position
- [ ] Can locate the runbook index without help
- [ ] Can state the severity definitions and who declares an incident
- [ ] Knows the escalation path and that escalating is a right, not a failure
- [ ] Knows what they are **not** authorised to do alone (`T4` actions per `_operation/SAFETY_TIERS.md`)

### Demonstrated

- [ ] Completed ≥3 shadow shifts spanning at least one weekend
- [ ] Executed ≥2 runbooks end-to-end in a non-production environment
- [ ] Participated in ≥1 incident in any role
- [ ] Ran a game-day scenario as primary with a mentor observing

## Shadow Rotation

Shadow means: paged simultaneously with the real primary, expected to diagnose independently,
with the primary as the actual owner.

| Shadow shift | Expectation |
|--------------|-------------|
| 1 | Observe; ask anything; no action taken |
| 2 | Diagnose independently, propose an action, primary executes |
| 3 | Execute under observation, primary present |

Shadowing without paging the shadow is not shadowing — it is a wiki tour. The point is the
3 a.m. notification and the state it puts a person in.

## First Solo Shift

Gate explicitly:

- Pair the first solo shift with an **experienced secondary** who knows they are the safety net.
- Schedule it on a weekday, not a weekend, and never during a freeze exit or a major release.
- Lower the escalation timeout for that shift (e.g. 3 minutes instead of 5).
- Debrief afterwards regardless of whether anything fired.

## Reverse Onboarding — Offboarding

When someone leaves the rotation, before their last shift:

- [ ] Remove from all escalation tiers, including ones they are only named in as a fallback
- [ ] Reassign carry-forward items they own
- [ ] Check whether they are the only escalation target anywhere — this is how silent gaps form
- [ ] Capture undocumented knowledge: what do they know that is not in a runbook?
- [ ] Recompute the pool size and per-person burden; if the pool drops below 6, raise it

The offboarding checklist is skipped more often than the onboarding one, and it is where
coverage gaps are actually created.

## Game Days

The only way to test readiness without waiting for an outage.

- Scope one failure mode, announced in advance for the first several rounds.
- Non-production first; production game days require `operation-change` approval and an
  explicit abort condition.
- The scoring question is not "did they fix it" but "did they find the runbook, follow it,
  and escalate at the right moment".
- Every game day that reveals a missing or wrong runbook produces a handoff to
  `operation-runbook`. That is the primary output, not the score.
