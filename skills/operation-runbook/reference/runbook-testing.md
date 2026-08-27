<!-- operation:deferred -->
# Runbook Testing

Purpose: Dry-run design, game-day validation, drift detection, audit verdicts.
Read when: dry-run design, game-day validation, drift detection, audit verdicts
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

An untested runbook is a hypothesis with formatting. Testing is what converts it into a control.

## Levels

| Level | What it proves | Cost | Cadence |
|-------|----------------|------|---------|
| Read-through | Steps are unambiguous, commands are syntactically right | Minutes | On write, and on every edit |
| Dry-run | Preconditions hold, permissions work, targets exist | Minutes | On write, before every reliance |
| Non-production execution | The procedure achieves the goal state | Hours | On write, then per review cadence |
| Production rehearsal (game day) | It works under real conditions, with real access, at real scale | Half a day | Per review cadence for T3. **T4: never rehearsed destructively in production** — see below |
| Incident execution | It works under pressure | — | Opportunistic; always debrief |

Only the last three update `last_executed`.

## Read-Through Protocol

Give the runbook to someone who **did not write it** and who has the required access. They read
it aloud and stop at every ambiguity. The author stays silent — the moment the author explains
a step, the test has failed for that step.

Record every stop. Each one is a defect: the responder at 3 a.m. has no author to ask.

## Dry-Run Design

A dry-run must exercise **every check the real run performs**:

- [ ] Authentication and authorisation — actually attempt, do not assume the grant
- [ ] Target existence and identity — confirm the resource and the environment
- [ ] Precondition state checks
- [ ] Input validation
- [ ] Prints exactly what would change, resource by resource

A dry-run that skips the permission check is worse than no dry-run: it produces confidence, then
the real run fails at step 9 leaving a partially-applied state.

## Game Days

The only way to test a runbook under conditions resembling reality.

**Design:**
- One failure mode per game day.
- Announce in advance for the first several rounds; unannounced only once the team is practised.
- Non-production first. Production game days require `operation-change` approval and an explicit
  abort condition agreed beforehand.
- **`T4` procedures are never rehearsed destructively in production.** Rehearsing an
  irreversible action for practice is indistinguishable from causing the incident. Rehearse them
  as: a full non-production run at production data volume, plus a production **dry-run** that
  exercises every check and stops before the mutating step, plus a read-through of the mutating
  step with the approver present. That combination is what `last_executed` records for a `T4`
  runbook.
- The executor is **not** the runbook's author.
- An observer records every hesitation, wrong turn, and out-of-band question.

**The scoring question is not "did they fix it".** It is:
- Did they find the runbook, and how long did it take?
- Did the steps work as written?
- Where did they stop, guess, or ask someone?
- Did they escalate at the right moment?

Every game day that reveals a missing or wrong runbook produces a handoff to author or fix it.
That is the primary output, not a score.

## Drift Detection

Runbooks break silently, because the document does not fail when the system changes underneath it.

Automatable checks:
- Command syntax validated against current CLI versions
- Referenced hosts, services, namespaces, and dashboards still resolve
- Linked URLs return 200
- Named alerts still exist in the alerting config
- Referenced flags and options still exist in `--help`
- Owners still present in the directory

Non-automatable, caught only by execution:
- Steps that succeed but no longer produce the intended effect
- Preconditions that have quietly become false
- Timings that have changed (a 30s wait that now needs 5 minutes)
- Behaviour that changed while the interface did not

## Post-Incident Runbook Review

After any incident where a runbook was used, ask:

- [ ] Was it found quickly? If not, the discoverability path is the defect.
- [ ] Did every step work as written? Record each divergence verbatim.
- [ ] Were there steps taken that are not in the runbook? Those are missing steps.
- [ ] Were there steps skipped? Those are either unnecessary or badly explained.
- [ ] Did the abort conditions cover what actually happened?
- [ ] Was the estimated duration right?

Update the runbook **within 48 hours**, while memory is intact. Runbook updates deferred to a
sprint boundary do not happen.

**Runbooks written during an incident are optimistic** — they capture what worked once, omitting
the four things tried first and the conditions that made it work. Revisit them when calm, and
add the conditions.

## Audit Checklist

Per runbook:

- [ ] Header contract complete, `last_executed` honest
- [ ] Owner is a named individual, still present
- [ ] Tier assigned, and consistent with the most dangerous step
- [ ] Abort conditions present
- [ ] Every mutating step has an inline reversal
- [ ] Every step has an expected observation and a divergence branch
- [ ] Verification section checks the **user path**, not just internal health
- [ ] Escalation names a person or role and a channel, with what to attach
- [ ] No credentials or secret values in the text
- [ ] Environment targeting explicit in every command
- [ ] Linked from the alert that should trigger it, if any
