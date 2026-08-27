<!-- operation:deferred -->
# Toil Accounting

Purpose: Applying the six-criteria toil test, scoring, prioritisation, toil budget enforcement.
Read when: applying the six-criteria toil test, scoring, prioritisation, toil budget enforcement
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## The Six Criteria

Work is toil only if **all six** hold. Work missing any one is something else, and calling it
toil dilutes the budget that protects against real toil.

| # | Criterion | Test |
|---|-----------|------|
| 1 | **Manual** | A human performs it by hand |
| 2 | **Repetitive** | It has been done before and will be done again |
| 3 | **Automatable** | A machine could do it — no judgement required |
| 4 | **Tactical** | Reactive and interrupt-driven, not strategic |
| 5 | **No enduring value** | The service is in the same state afterwards, not better |
| 6 | **Scales with service size** | More traffic, users, or instances means more of it |

## Not Toil

Commonly mislabelled:

| Work | Why not toil | What it is |
|------|--------------|------------|
| Debugging a novel failure | Fails 3 (requires judgement) | Engineering |
| Code review | Fails 5 (leaves the codebase better) | Engineering |
| Writing a runbook | Fails 2 and 5 | Investment that removes toil |
| Attending on-call | Fails 3 — but the *pages* may be toil | Overhead |
| Manual QA before release | Fails 5 arguably; usually automatable | Process debt |
| Answering the same support question | Passes all six | **Toil** |
| Manually restarting a service weekly | Passes all six | **Toil** |
| Provisioning access requests by hand | Passes all six | **Toil** |

Distinguish **toil** from **overhead** (meetings, admin, planning). Overhead is not eliminable
by automation, so measuring them together produces a number nobody can act on.

## Scoring

```
score = frequency_per_month
      × minutes_per_occurrence
      × growth_factor
      × error_risk
      ÷ automation_cost_hours
```

| Factor | Scale |
|--------|-------|
| `growth_factor` | 1.0 flat · 1.5 grows with usage · 2.5 grows with fleet size |
| `error_risk` | 1.0 harmless if fumbled · 2.0 causes a ticket · 4.0 causes an incident |
| `automation_cost_hours` | Honest engineering estimate including testing and maintenance |

Rank by score. Sanity-check the top of the list against "would we actually do this?" — a high
score on something executed twice a year is an artifact of the formula.

**Annual hours reclaimed** = `frequency_per_month × 12 × minutes ÷ 60`. This is the number that
funds the work; the score only orders the queue.

## Toil Budget

Cap toil at **≤50% of an operations-carrying team's time**. Above that, the team cannot invest
in reducing it, and toil compounds.

| Measured toil | Verdict | Action |
|---------------|---------|--------|
| <25% | Healthy | Continue |
| 25–50% | Acceptable | Track trend; reduce top items |
| 50–70% | Over budget | Stop accepting new operational surface until reduced |
| >70% | Critical | Escalate; the team is in a spiral it cannot exit unaided |

Measurement is by sampled self-report or time tracking over ≥2 weeks. An unmeasured toil claim
is `O5` (`_operation/CONTRACT.md`) — say so rather than asserting a percentage.

## Reduction Strategies, In Order

Try them in this order. Automation is third, not first.

1. **Eliminate** — why does the work exist at all? A weekly restart papering over a memory leak
   should produce a leak fix, not a cron job. Automating around a defect makes the defect permanent.
2. **Reduce frequency** — fix the underlying cause, change the threshold, batch the occurrences.
3. **Self-service** — move the work to the requester with a safe tool. Usually the largest win
   for access requests, environment provisioning, and data pulls.
4. **Automate** — via `reference/automation-ladder.md`.
5. **Delegate** — a managed service or another team. Genuine only if it removes the work rather
   than moving it.

**Automating toil that should have been eliminated is the most common mistake.** Ask "why does
this exist" before "how do we script it".

## What Will Not Be Automated

Every toil report explicitly lists deferrals with reasons. Silent omission reads as "everything
is covered" when it is not.

| Item | Annual hours | Why deferred |
|------|--------------|--------------|
| <name> | <n> | Below the automation-cost threshold / trigger requires judgement / underlying fix is scheduled instead |

## Reporting

Monthly, to the service owner:

- Measured toil percentage against the 50% budget, with the trend
- Top 5 toil sources by annual hours, with score and status
- Hours reclaimed by completed automation (the credibility of the next request depends on this)
- Deferral list with reasons
- New toil introduced this period, and by what — new operational surface arrives silently,
  usually with a launch
