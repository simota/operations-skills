<!-- operation:contract -->
# Safety Tiers

Classify proposed actions by blast radius and actual reversibility; approvals below are human.

**This set never executes system mutations**, including through delegated tools or with approval.
Permitted local artifacts and verified, bounded read-only observations are allowed.
A tool grant does not enforce this boundary; commands for changes remain human proposals.

## Tier Table

| Tier | Blast radius | Reversibility | Human operator approval | Required before human execution |
|------|--------------|---------------|----------|---------------------------|
| `T1` | Bounded read-only observation | No state change | Existing access policy; no additional tier approval | Verify identity, target, scope and read-only semantics; capture output |
| `T2` | Single service, one environment | Reversible within minutes (redeploy, flag flip) | Existing change policy; no additional tier approval; post-verify | Meaningful preflight + rollback command stated |
| `T3` | Multiple services, or customer-visible behaviour | Reversible but slow (hours) or partially lossy | Human confirmation required | Named approver + rollback rehearsed |
| `T4` | Irreversible mutation, destruction, or loss of access | Cannot be undone in place; recovery needs an external copy, or is impossible | Human invokes with two-person approval | Recovery path verified (table below) + two-person rule |

No dry run or reversal is required for a read-only observation. Read-only is not harmless:
PII access still follows rule 4, and expensive queries need a bounded load and timeout.
For `T2`, use a dry run only when it exists and tests the relevant risk; otherwise name
and verify the preconditions and bounded scope. Do not invent a dry-run command.

## Reversibility Decides the Tier, Not the Action Category

Only an exercised reversal permits a lower tier; classify the instance, not the action name.

| Action | `T4` when | Lower when |
|--------|-----------|------------|
| Data mutation / backfill | No verified down-path; the prior values are not recoverable | Prior values are preserved (dual-write, versioned column, snapshot taken and restore-tested) → `T2`–`T3` by blast radius |
| Cross-region failover | Failback is unexercised, or the regions diverge writes | Failback exercised within the tier's DR cadence and writes are single-primary → `T3` |
| Credential rotation | The old credential is revoked before the new one is confirmed | Old credential retained and revoked only after the new one is verified in use → `T3` |
| Deletion | Any | — deletion is always `T4` |
| Third-party side effect (charge, email, webhook) | Any | — never reversible; requires explicit acceptance, not approval |

## Recovery Prerequisite by Action Type

| Action | Verified recovery path means |
|--------|------------------------------|
| Data mutation / deletion | A backup covering the affected rows has been **restored** in a test, not merely taken |
| Credential rotation | The old credential is still valid and a rollback-to-old procedure is stated; revocation is a separate, later step |
| Cross-region failover | Failback has been exercised, and the divergence-reconciliation procedure is written |
| Restore-from-backup | The restore has been rehearsed against a copy at current data volume |
| Third-party side effect | No recovery path exists. Requires explicit written acceptance of the consequence by a named individual, in place of a recovery path |

## Classification Rules

1. **Take the highest tier that any single step reaches.**
2. **Unknown reversibility is `T4`.** Documented but unexercised reversals remain unknown.
3. **Reversibility is measured in restored user experience, not in reverted config.**
   Rolling back a deploy that already wrote a new schema version is not reversible.
4. **PII reads are `T3`**, auditable even though nothing changes.
5. **A `T4` action is never triggered by automation.** Human-invoked scripts are allowed;
   alerts, schedules, retries and remediation loops are not, including during incidents.

## Escalation During Incidents

Incident pressure does not lower a tier. It changes *who* approves, not *whether*:

| Situation | Normal approver | Incident approver |
|-----------|-----------------|-------------------|
| `T3` | Service owner | Incident Commander |
| `T4` | Service owner + change approver | Incident Commander + second responder (two-person rule holds) |

An unreachable approver means escalate, not proceed; record every tier-skip as a control failure.

## Emission

Label each proposed system mutation **PROPOSED — HUMAN EXECUTION** and emit:
For read-only observations, use a compact tier, target, query and coverage record instead;
`T3` reads still name their approver. A review with no proposed actions invents none.

```yaml
SAFETY_TIER:
  operator: "[human role or named operator, never the agent]"
  execution: proposed
  tier: T1 | T2 | T3 | T4
  rationale: "[why this tier — blast radius and reversibility]"
  preconditions: "[identity, target, state and policy checks before the human acts]"
  command: "[recommended command or procedure; not an agent tool invocation]"
  expected_observation: "[what should change, and where it will be observed]"
  abort_condition: "[observable condition requiring the operator to stop]"
  reversal: "[the exact command or procedure that undoes it, or NONE]"
  recovery: "[recovery/compensation and proof state; consequence acceptance if none]"
  approver: "[named role; or existing-policy reference for T1/T2]"
  verification: "[what proves the action worked]"
```

`reversal: NONE` on a **mutating** step below `T4` is a classification error — re-classify.
Read-only observations use `reversal: not applicable`, not unknown reversibility.
