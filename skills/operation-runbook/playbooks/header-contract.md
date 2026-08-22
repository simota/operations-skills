<!-- operation:guidance -->
# Runbook Header Contract, Automation Ladder

## Runbook Header Contract

Every runbook opens with this block. It is what a responder reads before deciding to proceed.

```yaml
runbook: <service>/<procedure-name>
purpose: "<the goal state, one line>"
trigger: "<alert name, symptom, or schedule>"
tier: T1 | T2 | T3 | T4          # max across all steps
approval: AUTONOMOUS | "<role>"  # required before step 1
duration: "<expected wall-clock>"
idempotent: yes | partial | no
dry_run: "<command>" | none
owner: "<named individual>"
last_executed: <YYYY-MM-DD> | UNVERIFIED
review_by: <YYYY-MM-DD>
abort_if:
  - "<condition that means stop, do not continue>"
```

`last_executed: UNVERIFIED` is a loud, deliberate warning. Do not remove it to make a document
look finished.

## Automation Ladder

| Rung | State | Gate to reach the next rung |
|------|-------|----------------------------|
| 0 | Tribal knowledge | Write it down at all |
| 1 | Documented procedure | Executed successfully twice by someone who did not write it |
| 2 | Scripted, human-invoked | Idempotent, dry-run mode exists, exits non-zero on failure |
| 3 | Self-service / one-click | Preconditions checked by the tool; blast radius bounded in code |
| 4 | Automated with human approval | Circuit breaker, escape hatch, full audit log |
| 5 | Fully automated remediation | ≥20 successful supervised runs, tier ≤ T2, verified rollback |

**Skipping rungs is the failure mode.** Automation built directly from rung 0 encodes tribal
knowledge that was never checked against reality. `T3` cannot exceed rung 4; `T4` cannot exceed
rung 2 — a `T4` action is scripted at most, and always human-invoked. Tiers follow
reversibility, not the action's name (`_operation/SAFETY_TIERS.md`): a backfill with an
exercised down-path is `T2`–`T3` and may go further up the ladder.
