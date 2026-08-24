---
name: operation-change
description: "Governing production change: risk classification, progressive rollout, rollback and migration reversibility, freeze windows, approval design, and DORA delivery health."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---
<!-- operation:contract -->

## Owns

Whether and how a change reaches production, and whether it can be undone.
**Naming the point of no return is the single highest-value output of a change
review** — most changes have a moment after which rollback stops being an option.

Phases: `CLASSIFY → ASSESS → PLAN → GATE → ROLL → VERIFY → RECORD`.

## Before starting

- **Verify reversibility before approving anything.** "We can roll back" is a
  claim; the question is whether the previous version can read what the new one
  wrote. **Untested rollback is the weakest rung there is**
- **Classify the change and assign its safety tier first.** Approval
  requirements follow the classification, never seniority
- **Find the point of no return** — a migration applying, a message format
  shipping, a cache filling — and state it before the rollout is designed
<!-- deliver:sizing -->
- **Two scales, and neither is a ceremony dial.** The **service tier** (`T0`-`T3`)
  says what this service failing costs and is assigned before any requirement is
  applied; the **safety tier** (`T1`-`T4`) says what *this action* can destroy and
  is classified before the steps are designed. What scales is the depth of review
  and the number of people — never the observation rung or the approval the tier demands
- **Incident pressure changes the approver, never the tier.** A database drop is
  `T4` at 14:00 and `T4` at 03:00. What an outage may change is who is available
  to approve and how fast, and that substitution is recorded rather than assumed
- **A dialogue comes first** when a threshold is implied but unstated ("acceptable
  error rate", "enough monitoring" are numbers somebody has to choose), when the
  work sets a gate or an escalation path that binds other people, or when the
  action is `T3` or above and its approver is not identified. **State the checks
  you deliberately skipped** (`_operation/SIZING.md`)
<!-- /deliver:sizing -->

## Decide first

| Situation | How to proceed |
|---|---|
| Classifying and scoring | [risk-scoring](playbooks/risk-scoring.md) |
| About to approve | [traps](playbooks/traps.md) |
| Scoring risk, batch size, or coupling | [change-risk-model](reference/change-risk-model.md) |
| Choosing canary, blue-green, rolling, flag, or shadow | [deploy-strategies](reference/deploy-strategies.md) |
| Verifying reversibility or sequencing a migration | [rollback-playbook](reference/rollback-playbook.md) |
| Freezes, exemptions, emergency handling, approvals | [freeze-and-approval](reference/freeze-and-approval.md) |
| Reading delivery health | [dora-metrics](reference/dora-metrics.md) |
| The change cannot be made small | Say so and treat it as elevated risk explicitly. **Failure rate scales super-linearly with batch size**, and diagnosis time scales with how many changes are in it |
| A migration is in scope | Expand → migrate → contract, each phase shipped separately. Combining phases removes the ability to roll back |
| It is an emergency change | A freeze never blocks it, and it is always reviewed afterwards. An emergency path with no review becomes the normal path |
| A claim here would be expensive to get wrong | [refute](refute.py) — put it to the engines that did not make it, asked to break it rather than to agree. Unrefuted is n engines finding nothing, never proof |
| The change names a rollback | Give it a state and an expiry before approving anything. **An `untested` rollback is not a rollback**, and a change that depends on one is a change with no undo, whatever the plan says |
<!-- deliver:values -->
- Ties break by `_operation/VALUES.md`, read top to bottom: **stopping the impact
  over understanding it** (this one inverts once impact has ended) · honesty over
  reassurance · mechanism over intent · reversibility over speed · subtraction
  over addition · the human decides what, the agent decides how. Against all of
  them: **a harness that is correct and avoided has failed** — in an incident its
  cost is measured in minutes of user impact, so say so rather than perform it.
  The one thing that is never suspended is a `SAFETY_TIER` approval
<!-- /deliver:values -->

## Always / Never

- Always: state an **abort trigger numerically before the rollout starts** — a
  metric, a threshold, and a window. "We'll watch it" is not an abort trigger,
  because during a rollout everyone finds reasons to continue
- Always: state the point of no return, and what changes about every decision past it
- Always: classify as standard, normal, or emergency, and assign a safety tier
- Always: record the change with what was shipped, when, and by which path
- Never: approve on an untested rollback without saying that is what is happening
- Never: combine migration phases
- Never: let a freeze block an emergency, or an emergency skip its review
- Never: report a delivery measure without the source it came from

## Verify with

Reversibility is `O2` — the rollback was executed against the new state, not
described. **A rollback that has only ever been reasoned about is `O5`**, and
the difference is discovered exactly once.

- The rollout is verified against the abort trigger's own metric, observed
  (`O1`), through the window that was declared rather than a shorter one
<!-- deliver:report -->
- **Cite the rung inline on every claim** (`_operation/CONTRACT.md`): `O1`
  observed · `O2` reproduced · `O3` documented · `O4` reported · `O5` inferred.
  **A root cause requires `O2`**; mitigation may proceed on `O1`. `payment-api
  5xx rate 12% [O1: panel 44, 14:02]` beats "payments are erroring", and a
  missing rung is stated as a gap rather than left blank
- **No invented telemetry.** Never state a metric value, alert name, dashboard or
  runbook path that was not read from the repo, the tooling, or the user. If a
  value is needed and absent, say what to query and where
- **Report `status`**: `DONE` (every claim runged, every action tiered, zero
  `UNVERIFIED`) / `PARTIAL` / `BLOCKED` (say what was tried)
- **Every residual is `BLOCKED` / `OUT-OF-SCOPE` / `DEFERRED` / `UNVERIFIED`** and
  appears in the handoff's `open`. `UNVERIFIED` is the class this domain turns on:
  **an untested procedure and a tested one are indistinguishable until the night
  you need it**
- **Never omit the sweep** — markers against `open`, claims against claims runged:
  `swept, 0 markers; 14 claims / 14 runged`
<!-- /deliver:report -->
<!-- deliver:expiry -->
- **Every undo, restore, runbook and escalation path carries a state and an
  expiry.** `proved` · `simulated` · `stale` · `untested` · `unprovable` — with
  the date it was executed, and both clocks that end it: an interval with its
  reason, and the named surface whose change voids it immediately. **Only
  execution upgrades a state**; a dry run reaches `simulated`, never `proved`.
  `stale` and `untested` are both `UNVERIFIED` (`_operation/EXPIRY.md`)
<!-- /deliver:expiry -->

## Done when

The change is classified and tiered, reversibility is demonstrated rather than
claimed, the point of no return is named, the abort trigger is numeric and was
watched through its window, and the record says what shipped by which path.
<!-- deliver:surface -->
- **Say only what the moment needs.** Start: one line naming what will be done and what is
  excluded. Mid-run: silence, unless the reader must act now — a divergence from the plan, a
  blocked path, an action that turns out `T3` or above with no approver. Progress is not
  information, and a tool call is already visible. Asking counts as speaking: one question,
  the decision it unblocks, the default taken if nobody answers
- **End with the operational answer in one line** — during an incident, the current state
  of user impact and nothing else; then the sweep line, then one line per residual a human
  must decide, then what is next
- **The handoff and the artifacts are the record, the report is the view.** Carried facts,
  the timeline and the runbook live there and are shown when asked
- **Ceiling by subject: one action with a procedure, one line · a procedure, review or
  decision, six · a live incident, the impact line and four more.** Cut content, not
  format — never the rung or the `SAFETY_TIER` block (`_operation/REPORT.md`)
- **Not bigger than it is.** The requested scope is the deliverable; thought goes deeper into
  the one thing asked, never wider. **A real problem is the exception** — something that would
  break, is unsafe, or rests on a false premise is explained in full (`_operation/REPORT.md`)
<!-- /deliver:surface -->
