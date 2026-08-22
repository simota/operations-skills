<!-- operation:contract -->
# Safety Tiers

Every operational action carries a blast radius. Classify before executing — the tier
decides who may run it, whether a human confirms, and what must be verified afterwards.

## Tier Table

| Tier | Blast radius | Reversibility | Autonomy | Required before execution |
|------|--------------|---------------|----------|---------------------------|
| `T1` | Single process / single replica / read-only | Instant, no state change | Autonomous | Dry-run output logged |
| `T2` | Single service, one environment | Reversible within minutes (redeploy, flag flip) | Autonomous with post-verify | Dry-run + rollback command stated |
| `T3` | Multiple services, or customer-visible behaviour | Reversible but slow (hours) or partially lossy | Human confirmation required | Named approver + rollback rehearsed |
| `T4` | Irreversible mutation, destruction, or loss of access | Cannot be undone in place; recovery needs an external copy, or is impossible | Human invokes; agent advises only | Recovery path verified (table below) + two-person rule |

## Reversibility Decides the Tier, Not the Action Category

The blast-radius column gives examples, not a fixed list. **Data mutation, cross-region
operations, and credential rotation are usually `T4` because they are usually irreversible —
not because of what they are called.** Where a specific instance has a reversal that has been
written down and exercised, classify it by that reversal:

| Action | `T4` when | Lower when |
|--------|-----------|------------|
| Data mutation / backfill | No verified down-path; the prior values are not recoverable | Prior values are preserved (dual-write, versioned column, snapshot taken and restore-tested) → `T2`–`T3` by blast radius |
| Cross-region failover | Failback is unexercised, or the regions diverge writes | Failback exercised within the tier's DR cadence and writes are single-primary → `T3` |
| Credential rotation | The old credential is revoked before the new one is confirmed | Old credential retained and revoked only after the new one is verified in use → `T3` |
| Deletion | Any | — deletion is always `T4` |
| Third-party side effect (charge, email, webhook) | Any | — never reversible; requires explicit acceptance, not approval |

Downgrading below `T4` on this table requires the reversal to be **exercised**, not merely
documented. An unexercised reversal is `unknown reversibility`, which is `T4` by rule 2.

## Recovery Prerequisite by Action Type

`T4` requires a **verified recovery path**, and what that means differs by action. A single
"backup verified restorable" requirement is unsatisfiable for actions that have no backup:

| Action | Verified recovery path means |
|--------|------------------------------|
| Data mutation / deletion | A backup covering the affected rows has been **restored** in a test, not merely taken |
| Credential rotation | The old credential is still valid and a rollback-to-old procedure is stated; revocation is a separate, later step |
| Cross-region failover | Failback has been exercised, and the divergence-reconciliation procedure is written |
| Restore-from-backup | The restore has been rehearsed against a copy at current data volume |
| Third-party side effect | No recovery path exists. Requires explicit written acceptance of the consequence by a named individual, in place of a recovery path |

## Classification Rules

1. **Take the highest tier that any single step reaches.** A runbook with nine `T1` steps
   and one `T4` step is a `T4` runbook.
2. **Unknown reversibility is `T4`.** If nobody can state how to undo the action, it is
   irreversible until proven otherwise.
3. **Reversibility is measured in restored user experience, not in reverted config.**
   Rolling back a deploy that already wrote a new schema version is not reversible.
4. **Production data reads are `T1` only if they exclude PII.** PII reads are `T3` — they
   are auditable events even though nothing changes.
5. **A `T4` action is never triggered by automation.** It may be *scripted* — a script a
   human invokes deliberately is fine, and is usually safer than the same steps typed by
   hand. What is forbidden is a `T4` action firing from an alert, a schedule, a retry, or a
   remediation loop. Not during an incident, not under time pressure, not "just this once".

## Escalation During Incidents

Incident pressure does not lower a tier. It changes *who* approves, not *whether*:

| Situation | Normal approver | Incident approver |
|-----------|-----------------|-------------------|
| `T3` | Service owner | Incident Commander |
| `T4` | Service owner + change approver | Incident Commander + second responder (two-person rule holds) |

If the approver cannot be reached, the correct action is to escalate, not to proceed.
Record every tier-skip as an incident action item — a skipped tier is a control failure
even when the outcome was fine.

## Emission

When any skill in this repo proposes or executes an action, it emits:

```yaml
SAFETY_TIER:
  tier: T1 | T2 | T3 | T4
  rationale: "[why this tier — blast radius and reversibility]"
  reversal: "[the exact command or procedure that undoes it, or NONE]"
  approver: "[role, or AUTONOMOUS]"
  verification: "[what proves the action worked]"
```

`reversal: NONE` on anything below `T4` is a classification error — re-classify.
