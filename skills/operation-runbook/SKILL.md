---
name: operation-runbook
description: "Writing procedure that works at 3 a.m.: runbook anatomy, preconditions and abort conditions, testing it, the automation ladder, and toil accounting."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---
<!-- operation:contract -->

## Owns

Procedure that a tired responder with no context can execute correctly. **Every
runbook is read under the worst cognitive conditions its author will never
experience while writing it.**

Phases: `SCOPE → CLASSIFY → DRAFT → TEST → AUTOMATE → GOVERN`.

## Before starting

- **Classify the safety tier before writing any step.** The tier decides whether
  the procedure needs approvals, a two-person rule, or must not be automated at
  all — and **the runbook's tier is the maximum of any single step's tier**
- **Find out whether anyone has actually done this.** A procedure assembled from
  what the code appears to do is a guess written in the imperative
- **Establish the preconditions and the abort conditions first.** A procedure
  with no stated way to stop is one that gets pushed through when it should not be
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
| The header contract, and how far up the automation ladder this goes | [header-contract](playbooks/header-contract.md) |
| About to write steps | [traps](playbooks/traps.md) |
| Structuring the document | [runbook-anatomy](reference/runbook-anatomy.md) |
| Deciding what deserves a runbook at all | [sop-catalog](reference/sop-catalog.md) |
| Proving it works | [runbook-testing](reference/runbook-testing.md) |
| Considering automation | [automation-ladder](reference/automation-ladder.md) |
| Justifying the work | [toil-accounting](reference/toil-accounting.md) |
| A step is not idempotent | Mark it explicitly and precede it with a state check. Every step says what happens when it is run twice |
| The procedure has never been executed | Mark the runbook `UNVERIFIED` in its header until it has. **An untested procedure and a tested one are indistinguishable until the night you need it** |
| A claim here would be expensive to get wrong | [refute](refute.py) — put it to the engines that did not make it, asked to break it rather than to agree. Unrefuted is n engines finding nothing, never proof |
| The runbook is written and looks complete | It is `untested` until somebody executes it. Record who ran it, in which environment, and what expires it — **the path that will be taken next time is the one that must be proved** |
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

- Always: write every step **imperative, singular, and verifiable** — one
  action, one expected observation. "Check the service is healthy" is not a
  step; "run `<cmd>`; expect `status: ok`" is
- Always: open with preconditions and abort conditions. **Abort conditions are
  non-negotiable**
- Always: name each mutating step's **reversal inline, beside the step** — not
  in a rollback section 200 lines down that nobody reaches under pressure
- Always: state what a step does when run twice
- Never: automate a procedure that has not been executed manually and
  successfully at least twice. **Automation of an unproven procedure encodes a
  guess and executes it faster**
- Never: write a step whose expected observation you cannot state
- Never: reference a command, path, or dashboard that was not read
- Never: let a tier be lowered because the procedure is now automated

## Verify with

A runbook is `O2` only once it has been executed against a real or staged
system and the observations matched. Reading it back is `O3` — documented, which
evidences that a procedure exists and nothing about whether it works.

- **Test by handing it to someone who did not write it.** Every step they have
  to ask about is a defect in the step, not in the reader
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

Every step is one action with one observation, preconditions and abort
conditions open the document, every mutating step names its reversal inline,
idempotency is stated per step, and the header says truthfully whether it has
ever been run.
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
