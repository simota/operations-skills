---
name: operation-oncall
description: "Making on-call survivable: rotation design, escalation policy, alert hygiene with an explicit verdict per alert, shift handoff, onboarding, and rotation health."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---
<!-- operation:contract -->

## Owns

Who gets woken, for what, and whether that is sustainable. **Every addition here
spends someone's nights**, which is why an alert that nobody can act on is
deleted rather than tuned.

Phases: `MEASURE → TRIAGE → STRUCTURE → POLICY → VERIFY`.

## Before starting

- **Audit before designing.** Never propose a rotation change without first
  measuring the current page load — **a redesign on unmeasured load moves the
  pain, it does not remove it**
- **Get the actual page history**, not a description of the rota. What people
  remember about being woken is `O4`, and it is systematically wrong about volume
- **Establish who carries the pager.** Risk appetite and what is worth being
  woken for belong to them, not to whoever is designing the rota
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
| Deciding an alert's fate, or reading rotation health | [paging](playbooks/paging.md) |
| About to change the rota | [traps](playbooks/traps.md) |
| Designing the rotation itself | [rotation-design](reference/rotation-design.md) |
| Escalation paths and who is next | [escalation-policy](reference/escalation-policy.md) |
| Working through the alert set | [alert-hygiene](reference/alert-hygiene.md) |
| The rota is unhealthy and you need the cause | [oncall-health](reference/oncall-health.md) — attribute before fixing |
| Passing the pager | [shift-handoff](reference/shift-handoff.md) |
| Bringing someone onto the rota | [onboarding](reference/onboarding.md) |
| An alert points at no procedure | It stays, conditionally — the missing runbook is a blocking gap, not a reason to delete a real signal |
| A claim here would be expensive to get wrong | [refute](refute.py) — put it to the engines that did not make it, asked to break it rather than to agree. Unrefuted is n engines finding nothing, never proof |
| The escalation policy is written or changed | An escalation path is proved by a page that reached a human, not by the tool agreeing with itself. Give the roster an expiry: it goes `stale` the moment the people change |
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

- Always: give **every alert in scope an explicit verdict** — keep, demote,
  delete, or merge. Nothing is left unclassified, and "leave as-is" is spelled
  keep, with a reason
- Always: page a human only when all four hold — user-visible or imminent
  impact, a human action changes the outcome, that action cannot be automated
  today, and the action is documented. **Which criterion fails decides the
  verdict**; they are not interchangeable
- Always: enforce the page budget, and when it is exceeded for two consecutive
  rotations, **attribute the cause before fixing anything**
- Always: state the current measured load beside any proposed change
- Never: tune an alert that nothing can be done about. Delete it
- Never: design a rotation that depends on one person being reachable
- Never: hand off a shift without the open state travelling with it
- Never: quote a page count nobody measured

## Verify with

Page load is `O1` — counted from the paging system, over a stated window. A
rotation claimed to be sustainable without that count is `O5`, and sustainable
is exactly the claim people are worst at estimating about their own rota.

- **Every verdict names which of the four criteria decided it.** A verdict
  without that is an opinion about an alert
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

Current load is measured and stated, every alert in scope carries a verdict and
the criterion behind it, the escalation path terminates in someone who is
actually reachable, and any budget breach is attributed before it is fixed.
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
