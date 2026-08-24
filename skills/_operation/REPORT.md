<!-- operation:contract -->
# Report Surface

Binding on every `operation-*` skill. The other axes decide what must be true; this one
decides **what reaches the reader**. A run that rungs every claim, tiers every action and
then returns forty lines has still failed at the last step: **a report that gets skimmed is
a report that did not happen**, and in this domain it is skimmed at 3 a.m. by someone who
has been awake for nineteen hours.

## Record and view are different objects

| Object | Holds | Read by |
|---|---|---|
| The handoff (`_operation/HANDOFF.md`) and the artifacts | Carried facts with their rungs, the timeline, the runbook, the whole `open` list | The next skill, and the person when they ask |
| The report | The operational answer, the evidence under it, what is unresolved | The person, now |

The report is a **view over** those records, never a second copy of them in prose. A handoff
rendered field by field is how "impact ended at 14:02" arrives as a page.

## The moments a run speaks

Four, and no others. Each owes something different, and **what is right at one moment is
noise at the next.**

| Moment | What it owes | Ceiling |
|---|---|---|
| **Start** | What will be done and what is excluded, with the tier if it is not obvious | one line |
| **A question** | The one decision that is blocked, and the default taken if nobody answers | one question, one line |
| **Mid-run** | Nothing — unless the reader must act now: a divergence from what was agreed, a path found blocked, work that would grow the scope, an action that turns out to be `T3` or above with no approver identified | one line each, or silence |
| **End** | The report below | the ceiling below |

**Progress is not information.** "checking the dashboards", "now reading the runbook", "looks
healthy" tell the reader nothing they can act on, and they cost the same attention as the line
that matters. A tool call is already visible; narrating it a second time is the commonest way a
run fills a screen while saying nothing.

**A question is not a status update.** Ask when guessing wrong would be expensive to undo, ask
one thing, and say what happens if the answer never comes.

## At the end — this order, every time

1. **The operational answer, one line.** During an incident this is the current state of
   user impact and nothing else. Otherwise: the status and what was decided or done
2. **The evidence, one line.** The sweep (`_operation/CONTRACT.md`), which already carries
   the counts: `swept, 0 markers; 14 claims / 14 runged`
3. **What is unresolved** — one line per residual needing a human decision. `BLOCKED` and
   `UNVERIFIED` always; `DEFERRED` and `OUT-OF-SCOPE` sit in the handoff and appear here
   only if the reader would act on them today
4. **What is next** — one line, or nothing if the answer is nothing

A run with nothing unresolved reports lines 1 and 2 and stops.

## Ceiling

The subject sets it, the way the tiers do — there is no ceremony dial here either.

| Subject | The whole report |
|---|---|
| One action with an existing procedure | one line |
| A procedure, a review, a rota, a decision | six lines, plus the artifact |
| A live incident | the impact line, then at most four more. The timeline is the record |

**Over the ceiling means cutting content, not reformatting it.** A table, a nested list and
a heading per check are the three ways a report grows while appearing to have been tightened.

- **Tables for decisions, prose for reasoning.** A severity call, a tier, a go/no-go: table.
  Why: prose, and only where the reader would act differently for knowing it
- **Every recommendation carries an observation rung**, and an action carries its
  `SAFETY_TIER` block (`_operation/SAFETY_TIERS.md`). These are content, not ceremony: they
  do not count against the ceiling, and they are never dropped to fit it
- **Name the gap.** Unknown is a valid output. Padding a checklist with `N/A` to look
  complete is a defect
- **No invented telemetry.** Never state a metric value, alert name, dashboard, or runbook
  path that was not read from the repo, the tooling, or the user. If a value is needed and
  absent, say what to query and where

## The deliverable is not the report

The runbook, the readiness review, the postmortem, the incident timeline is an artifact with
a location. The report names it and says in one line what it establishes; it does not
reproduce it. **Stakeholder comms is its own artifact with its own template** and is not
bounded by this file — what is bounded is what the person running the skill reads back.

## Not bigger than it is

The requested scope is the deliverable. Neighbouring concerns, future possibilities and general
principles are not folded into the answer, and a small ask does not come back as a survey.
**Being thoughtful and diverging are not the same thing** — thought goes deeper into the one
thing asked, never wider. Option lists are given when they were asked for, or when the choice is
the reader's to make.

**A real problem is the exception.** If the request would break something, is unsafe, or rests
on a false premise, say what is wrong, why, and the options, at whatever length that takes.
**Cut noise, never risk.**

## Never in a report

- A restatement of the request, or of what the run was about to do
- A closing summary of what was just said
- Checks the artifact already lists, or a walk through every rung awarded
- Narration of process: what was read, which dashboard was opened first, which tool ran
- Reassurance. "Everything looks good" is a claim with a rung or it is nothing

## Asked for more

Bounding the default is not withholding. Every field lives in the handoff and the artifacts,
and "how do we know", "what did you skip", "what happens if it fails" are answered from them
at whatever length the question deserves. **The long form is available on request; it is just
not the default.**
