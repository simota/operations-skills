<!-- operation:deferred -->
# Production Readiness Review

Purpose: Running a readiness review, verification methods, blocking criteria, verdict format.
Read when: running a readiness review, verification methods, blocking criteria, verdict format
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## Principles

- **Verify, do not ask.** Every item names its verification method. A ticked box sourced from a
  conversation is `O4` (`_operation/CONTRACT.md`) and does not certify anything.
- **Blocking or non-blocking, never "recommended".** A finding with no consequence is a
  suggestion, and suggestions do not survive a launch deadline.
- **Requirements come from the tier.** Applying the ST0 bar to an ST3 dashboard wastes everyone's
  time and teaches teams that the review is theatre.
- **State what was not covered.** A review implying coverage it did not perform is worse than a
  narrow one that is honest.

## Checklist

Blocking threshold is per tier — see `playbooks/verdict.md` § Tier Requirements.

The verification column names the evidence, not who produces it. This review is read-only: a
check that needs an action — a restore, a failover, a deploy, a triggered limit — is performed by
a person, and the reviewer reads its record (`_operation/SAFETY_TIERS.md`, Who executes).

### Observability

| Item | Verification | Blocking for |
|------|--------------|--------------|
| SLIs defined and instrumented | Query them and see real values | ST0, ST1 |
| SLO with error budget policy | Read the document; confirm the policy names consequences | ST0 |
| Paging alerts exist for each critical SLI | List alerts; map to SLIs; find the gaps | ST0, ST1, ST2 |
| **Every alert has fired at least once in a test** | Read the record of a deliberate trigger that reached a device | All tiers with paging |
| Dashboards exist and load | Open them; confirm panels return data | ST0, ST1 |
| Logs are structured, retained, and searchable for the incident window | Search for a known event | ST0, ST1 |
| Trace or correlation IDs propagate across service boundaries | Follow one request end to end | ST0, ST1 |

The single most common defect found here: the alert rule is correct and the **notification
routing is not**. Testing the rule without testing delivery proves nothing.

### Response

| Item | Verification | Blocking for |
|------|--------------|--------------|
| On-call rotation exists with capacity for this service | Confirm with `operation-oncall`; check pool size | ST0, ST1, ST2 |
| Escalation path defined and exercised | Read the record of a no-acknowledge test | ST0, ST1 |
| A runbook for every paging alert; at ST0 each `proved` within expiry, or `unprovable` with a named compensating control, or `simulated` within expiry with the gap stated, by the rehearsal `operation-runbook` prescribes for a `T4` step never run in production | Read each header's `state` and `last_executed`; a person executes one end to end | ST0, ST1 |
| Runbooks for the top failure modes | Read them; record each one's state | ST2 |
| Every paging alert links to a specific runbook | Follow each link | ST0, ST1 |
| Severity definitions and declaration criteria agreed | Read them | ST0, ST1 |
| Communication path to support and customers exists | Confirm the channel and the owner | ST0, ST1 |

### Recovery

| Item | Verification | Blocking for |
|------|--------------|--------------|
| Rollback procedure documented and **exercised** | Read its last execution and record the state — a non-production run is `simulated`, and ST0/ST1 need `proved` within the tier's cadence, or the gap accepted as a risk | ST0, ST1 |
| **RPO defined** — how much data the business accepts losing | Read the figure; confirm the owner agreed it | ST0, ST1 |
| **RTO defined** — how long recovery may take | Read the figure; confirm the owner agreed it | ST0, ST1 |
| Backup frequency actually satisfies the RPO | Compare schedule to RPO — hourly backups cannot meet a 5-minute RPO | ST0, ST1 |
| Measured restore time actually satisfies the RTO | Compare the rehearsed restore duration to RTO, at current data volume | ST0, ST1 |
| Backups exist | List them; check the schedule | ST0, ST1, ST2 |
| **Backups have been restored successfully** | Read the record of a restore and its integrity check | ST0, ST1 |
| DR / failover tested within the tier's cadence | Confirm the test date and result | ST0, ST1 |
| **Failback** exercised, not just failover | Confirm the failback test date | ST0, ST1 |
| Replication lag is measurable and alerted on | Query it; find the alert | ST0, ST1 |
| Write topology is single-primary, or divergence reconciliation is documented | Read the design | ST0, ST1 |
| Fencing procedure exists for the old primary | Read it; confirm it was exercised | ST0 |
| Data repair procedure for the known corruption modes | Read it; confirm it is owned | ST0 |
| Graceful degradation when each dependency fails | Read the record of one dependency failed and the result observed | ST0, ST1 |

An untested backup is not a backup. Restore is the only verification that counts.

**RPO and RTO before backup mechanics.** "We have backups" answers nothing without the two
figures that make it assessable: how much data may be lost, and how long recovery may take.
A backup schedule that cannot meet the stated RPO, or a restore that has never been timed
against the RTO at current data volume, is a blocking finding even when backups exist and
restore successfully.

### Change

| Item | Verification | Blocking for |
|------|--------------|--------------|
| Deploy pipeline with automated verification | Read a recent deploy's verification output | ST0, ST1, ST2 |
| Progressive rollout available (canary or flags) | Confirm the mechanism exists and works | ST0, ST1 |
| Migration strategy follows expand-contract | Review the last migration | ST0, ST1 |
| Change record produced automatically | Check the log | ST0, ST1 |

### Capacity and Cost

| Item | Verification | Blocking for |
|------|--------------|--------------|
| Load tested to the tier's headroom multiple | Test results with the saturation point named | ST0, ST1 |
| The **next ceiling** is identified with a value | Read the analysis | ST0, ST1 |
| Autoscaling limits set, and the ceiling is known | Read the config | ST0, ST1 |
| Rate limiting or load shedding exists | Read the record of it engaging | ST0, ST1 |
| Cost per unit known, with its trend | Read the analysis | ST0, ST1 |

### Dependencies and Ownership

| Item | Verification | Blocking for |
|------|--------------|--------------|
| Dependency graph mapped, each node tiered | Read it; check for omitted infrastructure | ST0, ST1 |
| No dependency tiered below this service | Compare tiers | ST0, ST1, ST2 |
| Third-party dependencies have documented failure behaviour | Read it | ST0, ST1 |
| Named individual owner, with a backup | Confirm both are current employees | All |
| Knowledge is not concentrated in one person | Ask who else can operate it, then verify | ST0, ST1 |

## Verdict

One of the three verdicts `_operation/CONTRACT.md` § Verdicts defines — `GO`,
`GO-WITH-CONDITIONS`, `NO-GO` — read against the blocking findings above.

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
