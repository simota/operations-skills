<!-- operation:deferred -->
# Operational Maturity

Purpose: Scoring detection / response / recovery / prevention / knowledge, finding the weakest dimension.
Read when: scoring detection / response / recovery / prevention / knowledge, finding the weakest dimension
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

Five dimensions, scored 1–5. The value is in finding the **weakest** dimension — maturity is
limited by its minimum, not described by its average.

## Dimensions

### Detection — do we know when it breaks?

| Level | State |
|-------|-------|
| 1 | Customers report it first |
| 2 | Alerts exist, mostly on causes; many are noise |
| 3 | Symptom-based alerts on the main user paths |
| 4 | SLI-based alerting with burn rates; every critical SLI is covered |
| 5 | Detection gaps are found proactively and closed before they fire |

### Response — how well do we handle it?

| Level | State |
|-------|-------|
| 1 | Whoever notices, improvises |
| 2 | An on-call rotation exists; response is ad hoc |
| 3 | Severity levels and declaration criteria; roles assigned at SEV1 |
| 4 | Consistent incident command, real-time timeline, communication cadence held |
| 5 | Response is practised; game days; command transfer is routine |

### Recovery — how fast do we restore?

| Level | State |
|-------|-------|
| 1 | Recovery is improvised each time |
| 2 | Rollback exists in principle, rarely exercised |
| 3 | Rollback exercised; runbooks for the main failure modes |
| 4 | Progressive rollout with automated abort; verified restore from backup |
| 5 | Automated remediation for known patterns; DR exercised on a cadence |

### Prevention — does the same thing recur?

| Level | State |
|-------|-------|
| 1 | The same failures recur, unremarked |
| 2 | Postmortems written for the largest incidents |
| 3 | Blameless postmortems with owned action items |
| 4 | Action items tracked to completion; repeat incidents are rare |
| 5 | Cross-incident patterns drive systemic change; failures are anticipated |

### Knowledge — what happens when a key person is unavailable?

| Level | State |
|-------|-------|
| 1 | One person knows how it works |
| 2 | Some documentation; largely stale |
| 3 | Runbooks for the main procedures, owned |
| 4 | Documentation is tested and current; several people can operate it |
| 5 | Anyone on the rotation can operate it; knowledge transfer is routine |

## Scoring

- Score from **evidence**, not from self-assessment. Ask for the artifact.
- Score the current state, not the intended one.
- A dimension is only at level N when **every** item at that level is true.

## Interpreting

| Pattern | Reading | Highest-leverage next action |
|---------|---------|------------------------------|
| Detection 1–2, everything else higher | Blind; strengths cannot be applied because nothing is noticed | Symptom-based alerting on critical user paths |
| Response high, Prevention low | Excellent firefighting, no learning | Postmortem action items tracked to completion |
| Recovery low, Detection high | Fast to know, slow to fix | Exercise rollback; write the top failure-mode runbooks |
| Knowledge 1–2 | Single point of human failure; every other score is fragile | Runbooks and a second operator |
| All at 3 | Healthy plateau | Pick the dimension with the highest incident cost |
| Prevention 5, Detection 2 | Implausible — re-score; you cannot prevent what you do not detect | Re-verify Detection with evidence |

**Give one action, not five.** Five parallel improvement plans is how maturity assessments
produce no improvement.

## Knowledge Is Load-Bearing

Knowledge at level 1–2 caps every other dimension in practice: alerts nobody understands are
noise, runbooks nobody has run are fiction, and a rotation where one person handles every
escalation is not a rotation.

When Knowledge is the weakest dimension, fix it first regardless of what else scores lower on
paper.

## Reassessment

- Annually, and after any incident revealing a systemic gap.
- Score the same way each time — drifting criteria produce fictional improvement.
- Track the **minimum** dimension over time. That trend is the maturity trend; the average is
  a comfort number.
