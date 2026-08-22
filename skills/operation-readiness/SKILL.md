---
name: operation-readiness
description: "Deciding whether a service is fit to run: service tiering, production readiness review, capacity and its known ceiling, maturity, handover, and decommission."
allowed-tools: Read, Grep, Glob, Bash
---
<!-- operation:contract -->

## Owns

Whether a service should be running, who operates it, and what happens when it
should not be any more. **Report-only** — it produces the verdict and the
findings, never the fixes.

Phases: `TIER → INVENTORY → ASSESS → VERIFY → VERDICT → HANDOVER`.

## Before starting

- **Assign the service tier first.** Every requirement derives from it, and a
  review that applies one bar to a payment path and an internal dashboard either
  blocks the dashboard needlessly or waves the payment path through
- **Get the evidence, not the assertions.** "Monitoring is in place" is `O4`; a
  screenshot of the alert firing in a test is `O1`
- **Establish who accepts risk** before the verdict is written. A blocking
  finding that gets overridden needs a named person, not a reclassification
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
| Issuing the verdict, or applying tier requirements | [verdict](playbooks/verdict.md) |
| About to grade a finding | [traps](playbooks/traps.md) |
| Assigning the tier | [service-tiering](reference/service-tiering.md) |
| Working the review itself | [prr-checklist](reference/prr-checklist.md) |
| Judging how far along the service is | [maturity-model](reference/maturity-model.md) |
| Capacity and what it costs | [capacity-and-cost](reference/capacity-and-cost.md) |
| Handing the service to another team | [handover-package](reference/handover-package.md) |
| Turning a service off | [decommission](reference/decommission.md) |
| A component appears in three or more postmortems | That is a **systemic finding**, escalated as a fitness question — not another per-incident action item on a pile |
| The launch will proceed with a blocking finding open | Record it as an accepted risk with a named individual and a review date. **Do not reclassify it as non-blocking** |
| A claim here would be expensive to get wrong | [refute](refute.py) — put it to the engines that did not make it, asked to break it rather than to agree. Unrefuted is n engines finding nothing, never proof |
| The review asks whether the service can be operated | Every capability claimed gets a state and an expiry, and the review reports the expired ones by name. **A readiness review that accepts undated proof has certified a document** |
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

- Always: mark findings **blocking or non-blocking, never "recommended"**. A
  finding with no consequence attached is a suggestion, and suggestions do not
  survive a launch deadline
- Always: give every checklist item its **verification method**, named
- Always: state capacity as a **known ceiling** — "it has been load tested to
  4× current peak, and the connection pool is the next limit", never "it scales"
- Always: treat handover as complete only when **the receiving team has operated
  the service without the building team, demonstrated**. State the demonstration
- Never: edit anything. Findings go to the skill that owns the gap
- Never: let a blocking finding become non-blocking because a date is close
- Never: pass an item on assertion where a `O1` observation was available
- Never: hand over on documents delivered

## Verify with

Every checklist item carries the rung its evidence reached and the method that
produced it. **The gap between `O4` and `O1` is this skill's entire job**: a
review that accepts what it was told has certified the telling, not the service.

- **A blocking verdict is defensible or it is noise.** Each blocking finding
  names the consequence it carries, not the standard it fails
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

The tier is assigned and every requirement derives from it, each item names its
verification method and the rung it reached, findings are blocking or
non-blocking with consequences attached, capacity states a known ceiling, and
any accepted risk names a person and a review date.
