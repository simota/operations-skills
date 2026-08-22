<!-- operation:deferred -->
# Production Readiness Review

Purpose: Running a readiness review, verification methods, blocking criteria, verdict format.
Read when: running a readiness review, verification methods, blocking criteria, verdict format
Verified: 2026-08-21 — no automated check.

## Principles

- **Verify, do not ask.** Every item names its verification method. A ticked box sourced from a
  conversation is `O4` (`_operation/CONTRACT.md`) and does not certify anything.
- **Blocking or non-blocking, never "recommended".** A finding with no consequence is a
  suggestion, and suggestions do not survive a launch deadline.
- **Requirements come from the tier.** Applying the T0 bar to a T3 dashboard wastes everyone's
  time and teaches teams that the review is theatre.
- **State what was not covered.** A review implying coverage it did not perform is worse than a
  narrow one that is honest.

## Checklist

Blocking threshold is per tier — see `reference/service-tiering.md`.

### Observability

| Item | Verification | Blocking for |
|------|--------------|--------------|
| SLIs defined and instrumented | Query them and see real values | T0, T1 |
| SLO with error budget policy | Read the document; confirm the policy names consequences | T0 |
| Paging alerts exist for each critical SLI | List alerts; map to SLIs; find the gaps | T0, T1, T2 |
| **Every alert has fired at least once in a test** | Trigger deliberately; confirm the page arrived on a device | All tiers with paging |
| Dashboards exist and load | Open them; confirm panels return data | T0, T1 |
| Logs are structured, retained, and searchable for the incident window | Search for a known event | T0, T1 |
| Trace or correlation IDs propagate across service boundaries | Follow one request end to end | T0, T1 |

The single most common defect found here: the alert rule is correct and the **notification
routing is not**. Testing the rule without testing delivery proves nothing.

### Response

| Item | Verification | Blocking for |
|------|--------------|--------------|
| On-call rotation exists with capacity for this service | Confirm with `operation-oncall`; check pool size | T0, T1, T2 |
| Escalation path defined and exercised | Run a no-acknowledge test | T0, T1 |
| Runbooks for the top failure modes, status `CURRENT` | Execute one end to end | T0, T1 |
| Every paging alert links to a specific runbook | Follow each link | T0, T1 |
| Severity definitions and declaration criteria agreed | Read them | T0, T1 |
| Communication path to support and customers exists | Confirm the channel and the owner | T0, T1 |

### Recovery

| Item | Verification | Blocking for |
|------|--------------|--------------|
| Rollback procedure documented and **exercised** | Run it in a non-production environment | T0, T1, T2 |
| **RPO defined** — how much data the business accepts losing | Read the figure; confirm the owner agreed it | T0, T1 |
| **RTO defined** — how long recovery may take | Read the figure; confirm the owner agreed it | T0, T1 |
| Backup frequency actually satisfies the RPO | Compare schedule to RPO — hourly backups cannot meet a 5-minute RPO | T0, T1 |
| Measured restore time actually satisfies the RTO | Compare the rehearsed restore duration to RTO, at current data volume | T0, T1 |
| Backups exist | List them; check the schedule | T0, T1, T2 |
| **Backups have been restored successfully** | Perform a restore; verify data integrity | T0, T1 |
| DR / failover tested within the tier's cadence | Confirm the test date and result | T0, T1 |
| **Failback** exercised, not just failover | Confirm the failback test date | T0, T1 |
| Replication lag is measurable and alerted on | Query it; find the alert | T0, T1 |
| Write topology is single-primary, or divergence reconciliation is documented | Read the design | T0, T1 |
| Fencing procedure exists for the old primary | Read it; confirm it was exercised | T0 |
| Data repair procedure for the known corruption modes | Read it; confirm it is owned | T0 |
| Graceful degradation when each dependency fails | Fail one dependency; observe | T0, T1 |

An untested backup is not a backup. Restore is the only verification that counts.

**RPO and RTO before backup mechanics.** "We have backups" answers nothing without the two
figures that make it assessable: how much data may be lost, and how long recovery may take.
A backup schedule that cannot meet the stated RPO, or a restore that has never been timed
against the RTO at current data volume, is a blocking finding even when backups exist and
restore successfully.

### Change

| Item | Verification | Blocking for |
|------|--------------|--------------|
| Deploy pipeline with automated verification | Run a deploy | T0, T1, T2 |
| Progressive rollout available (canary or flags) | Confirm the mechanism exists and works | T0, T1 |
| Migration strategy follows expand-contract | Review the last migration | T0, T1 |
| Change record produced automatically | Check the log | T0, T1 |

### Capacity and Cost

| Item | Verification | Blocking for |
|------|--------------|--------------|
| Load tested to the tier's headroom multiple | Test results with the saturation point named | T0, T1 |
| The **next ceiling** is identified with a value | Read the analysis | T0, T1 |
| Autoscaling limits set, and the ceiling is known | Read the config | T0, T1 |
| Rate limiting or load shedding exists | Trigger it | T0, T1 |
| Cost per unit known, with its trend | Read the analysis | T0, T1 |

### Dependencies and Ownership

| Item | Verification | Blocking for |
|------|--------------|--------------|
| Dependency graph mapped, each node tiered | Read it; check for omitted infrastructure | T0, T1 |
| No dependency tiered below this service | Compare tiers | T0, T1, T2 |
| Third-party dependencies have documented failure behaviour | Read it | T0, T1 |
| Named individual owner, with a backup | Confirm both are current employees | All |
| Knowledge is not concentrated in one person | Ask who else can operate it, then verify | T0, T1 |

## Verdict

| Verdict | Meaning |
|---------|---------|
| `GO` | No blocking findings |
| `GO WITH CONDITIONS` | Blocking findings resolved before launch, or accepted with a named accepter |
| `NO-GO` | Blocking findings unresolved and unaccepted |

`NO-GO` always states exactly what would change it to `GO`. A verdict that does not name the
path forward is an obstacle, not a control.

## Accepted Risks

When launching with an unresolved blocking finding:

```yaml
risk: "<the blocking finding>"
consequence: "<what happens when this fires — specific>"
accepted_by: "<named individual with the authority to accept it>"
accepted_on: <YYYY-MM-DD>
review_by: <YYYY-MM-DD>
compensating_control: "<what reduces the risk in the meantime, or NONE>"
```

Never reclassify a blocking finding as non-blocking to avoid this record. **The record is the
control** — it is what makes the trade-off visible when the risk fires six months later.

## Review Health

Track across reviews:

| Signal | Interpretation |
|--------|----------------|
| Share of reviews with ≥1 blocking finding | Approaching zero means the checklist has stopped checking |
| Accepted risks that later caused incidents | Calibration of the blocking threshold |
| Time from review to launch | Very short means the review is a formality appended to a decision already made |
| Findings resolved vs accepted | A rising acceptance share means the bar is being negotiated, not met |
