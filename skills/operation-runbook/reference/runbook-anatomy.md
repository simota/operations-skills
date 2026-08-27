<!-- operation:deferred -->
# Runbook Anatomy

Purpose: Structuring a runbook, writing verifiable steps, preconditions, abort conditions, inline rollback.
Read when: structuring a runbook, writing verifiable steps, preconditions, abort conditions, inline rollback
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## Full Structure

```markdown
---
runbook: payments-api/rollback-failed-deploy
purpose: "Return payments-api to the last known-good revision"
trigger: "PaymentsAPIErrorRateHigh, or manual after a bad deploy"
tier: T2
approval: AUTONOMOUS
duration: "5-8 minutes"
idempotent: yes
dry_run: "deploy rollback --dry-run --service payments-api"
owner: "<named individual>"
last_executed: 2026-08-14
review_by: 2026-11-14
abort_if:
  - "A database migration ran with the deploy and is not backwards-compatible"
  - "The last known-good revision is older than 30 days"
  - "Error rate is rising while no deploy occurred in the last 24h — wrong runbook"
---

## When to use this
<One paragraph. What symptom, and — critically — when NOT to use it.>

## Do not use this when
- <Situation that looks similar and needs a different procedure, with a link to it>

## Preconditions
- [ ] <Access or state required, with the command to verify it>
- [ ] <...>

## Steps

### 1. <Imperative action>
```
<exact command>
```
**Expect:** `<exact expected output or observable state>`
**If different:** <specific branch — another step number, another runbook, or escalate to whom>
**Reversal:** `<command>` | Not applicable (read-only)
**Tier:** T1

### 2. ...

## Verification
- [ ] <User-path check — the only proof that matters>
- [ ] <SLI check with named metric and threshold>
- [ ] <Side-effect check: queues drained, no retry backlog>

## Rollback
<Full procedure to undo everything, for the case where the runbook itself made things worse.>

## Escalation
If this procedure does not resolve the symptom: escalate to <named role> via <channel>,
attaching: <the specific outputs from steps N, M>.

## Notes
<Known quirks. Why a surprising step exists. Links to the incident that produced this runbook.>
```

## Writing Verifiable Steps

Each step is: **one action → one expected observation → one divergence branch.**

| Bad | Good |
|-----|------|
| "Check the service is healthy" | "Run `curl -s localhost:8080/healthz`; expect `{"status":"ok"}`" |
| "Restart if needed" | "If step 2 returned non-`ok`, run `systemctl restart payments-api`" |
| "Wait for it to come up" | "Poll `/healthz` every 5s for up to 60s; expect `ok` within 30s. If not `ok` at 60s → step 7" |
| "Verify the fix worked" | "Submit a test transaction via `<cmd>`; expect HTTP 201 and an order id" |
| "Scale up the service" | "`aws ecs update-service --cluster prod --service payments-api --desired-count 6`; expect `runningCount` 6 within 90s" |

**A step without an expected observation cannot fail visibly.** It produces a responder who
continues past a failed step into a partially-applied state — the hardest thing to recover from.

## Preconditions

Preconditions are **verified, not assumed**. Each carries the command that proves it:

- Access: `<cmd to confirm the permission actually works>` — granted is not the same as working
- System state: the runbook's assumptions about what is currently true
- Environment: which cluster/region/account, and how to confirm you are pointed at it
- Timing: is this safe during a freeze, during peak, during a migration?
- Dependencies: what must be healthy for this procedure to work at all

**The environment check is the most important precondition.** Most damaging runbook errors are
correct procedures executed against the wrong environment.

## Abort Conditions

The section most often missing, and the one that prevents the worst outcomes. State conditions
under which the responder **stops and escalates instead of continuing**:

- A precondition is false and cannot be made true.
- A step's output diverges in a way not covered by a branch.
- The symptom does not match what the runbook was written for.
- A `T3`+ step is reached and the approver is unreachable.
- The system is in a state the runbook does not describe.

Write them as a checklist at the top, before the steps. A responder must see the exits before
entering the procedure.

## Idempotency

| Value | Meaning | Requirement |
|-------|---------|-------------|
| `yes` | Every step safe to re-run; running twice equals running once | Verified by running twice and diffing state |
| `partial` | Some steps are not re-runnable | Each such step marked, preceded by a state check |
| `no` | Re-running causes harm | Requires an explicit "resuming from step N" section |

For `partial` and `no`, include a **resumption table**:

| Failed at | Current state | Resume from |
|-----------|---------------|-------------|
| Step 3 | Config applied, not reloaded | Step 4 |
| Step 5 | Traffic drained, replica not replaced | Step 5 (safe to repeat) |

Failure mid-procedure is the normal case, not the exception. A runbook with no resumption
guidance forces a responder to reason about partial state under pressure.

## Inline Reversal

Every mutating step names its reversal **on the step**, not in a distant rollback section.
Under pressure, nobody scrolls.

```
### 4. Drain traffic from the affected instance
`aws elbv2 deregister-targets --target-group-arn $TG --targets Id=$INSTANCE`
**Expect:** the target reaches `draining` in `describe-target-health`
**Reversal:** `aws elbv2 register-targets` with the same arguments
**Tier:** T2
```

A mutating step with `Reversal: NONE` must be `T4` and carry an approval gate — if it is not,
the classification is wrong.

## Writing for 3 a.m.

- **Front-load the decision.** "When to use" and "Do not use" come before any command.
- **No prose paragraphs inside steps.** Command, expectation, branch. Explanation goes in Notes.
- **Absolute over relative.** Full paths, explicit namespaces, explicit context flags. Never
  "in the right directory".
- **Copy-pasteable commands**, in fenced code blocks, with placeholders in obvious `<ANGLE>` form.
- **Numbers, not adjectives.** "Wait 30 seconds", not "wait a moment".
- **One page to the first action.** If the responder must scroll before doing anything, the
  preamble is too long.
- **State the total expected duration** in the header. A responder needs to know at step 2
  whether this is a 5-minute or a 2-hour procedure.
