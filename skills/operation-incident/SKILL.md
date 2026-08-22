---
name: operation-incident
description: "Running an incident while it is happening: declaring, command roles, impact assessment, mitigation before diagnosis, comms, and the postmortem afterwards."
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---
<!-- operation:contract -->

## Owns

The response while impact is live, and the learning after it ends. **Mitigation
outranks diagnosis**: until user-visible impact stops, every decision is judged
on whether it shortens impact.

Phases: `DECLARE → COMMAND → ASSESS → MITIGATE → VERIFY → COMMUNICATE → LEARN`.

## Before starting

- **Lead with the current state of user impact.** During an incident the first
  line is impact and nothing else — who is affected, since when, how badly
- **Declare early.** A wrongly-declared incident costs a meeting; an undeclared
  one costs the outage plus the delay. Say explicitly that false declarations
  are not penalised, because otherwise nobody believes it
- **Establish there is exactly one commander.** If two people are directing,
  the response has no command — say so and resolve it before anything else
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
| Declaring, and holding the live state | [declaring](playbooks/declaring.md) |
| About to act under pressure | [traps](playbooks/traps.md) |
| Calling severity | [severity-matrix](reference/severity-matrix.md) |
| Deciding who does what | [command-structure](reference/command-structure.md) — **the commander does not debug.** A commander with their hands in a terminal has stopped commanding |
| Choosing what to try | [mitigation-playbook](reference/mitigation-playbook.md) |
| Sizing the blast radius | [impact-assessment](reference/impact-assessment.md) |
| About to re-run a playbook, replace an instance, or roll a group | [capture-commands](reference/capture-commands.md) — convergence erases the divergence you were explaining, and an autoscaler destroys evidence on a clock you do not control |
| Citing command output as `O1`, or calling the mitigation done | [observation-traps](reference/observation-traps.md) — `changed=` is a module's claim rather than an observation, `--dry-run` reports success as an error, and the account is ambient |
| Telling people | [comms-templates](reference/comms-templates.md) — drop hedging entirely. Ambiguity costs minutes |
| Afterwards | [postmortem](reference/postmortem.md) |
| A diagnostic line of enquiry is running long | Time-box it — 15 minutes at the top severity — and at expiry say what it cost and pick another. Unbounded enquiry is how mitigation stops happening |
| No scribe is available | Mitigation proceeds and the commander timestamps decisions in the channel until one arrives. Waiting for a scribe violates mitigation-first |
| A claim here would be expensive to get wrong | [refute](refute.py) — put it to the engines that did not make it, asked to break it rather than to agree. Unrefuted is n engines finding nothing, never proof |
| A mitigation depends on a documented path | Check its state first — a `stale` or `untested` path chosen under pressure is where an incident acquires a second incident. Expired proof is treated as absent, not as probably fine |
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

- Always: assign a scribe at the top two severities **in parallel with**
  mitigation, never before it. A timeline reconstructed later is `O4` and will
  be wrong about ordering
- Always: give every action a `SAFETY_TIER`. **Incident pressure changes the
  approver, never the tier**
- Always: record every timestamp in UTC with the local offset stated once.
  Mixed-zone timelines are the single most common cause of a wrong sequence
- Always: reconcile every reported time against an observed one before the
  postmortem closes
- Never: let the commander debug
- Never: call something a root cause without `O2`. Anything else is a hypothesis
  and is labelled as one
- Never: state a metric, alert, dashboard or runbook path that was not read
- Never: close on a mitigation nobody watched take effect

## Verify with

Impact ending is `O1` — the metric that showed the impact now shows it gone,
observed, not assumed. **A mitigation that appeared to work and nobody can say
why is a finding**, not a loose end: it means the next occurrence is unhandled.

- The postmortem's timeline is `O1` throughout or says where it is not.
  `O4` never survives a postmortem unchallenged
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

Impact has ended and been observed to end, the timeline reconciles reported
times against observed ones, the cause is `O2` or explicitly a hypothesis, every
action carries its tier, and what remains unverified is named.
