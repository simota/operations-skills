<!-- operation:deferred -->
# Change Risk Model

Purpose: Classifying a change, scoring risk, batch-size effects, coupling and novelty assessment.
Read when: classifying a change, scoring risk, batch-size effects, coupling and novelty assessment
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## Classification

| Class | Definition | Approval | Record |
|-------|------------|----------|--------|
| `Standard` | Pre-approved, runbooked, executed unchanged before, low risk score | None | Logged automatically |
| `Normal` | New or modified change with lead time | Service owner | Change record before shipping |
| `Emergency` | Required to restore or protect service now | IC during an incident | Change record **after**, reviewed within 5 business days |

**Standard changes need an explicit list.** A class that exists in principle but names no
actual changes provides no benefit — everything routes to `Normal` and the process is slow
enough that people work around it.

Promote a `Normal` change to `Standard` after ~5 identical successful executions with no
incidents. Demote back on any change-caused incident.

## Risk Dimensions

Score 1–5 each. Any single 5 forces `T3`+ handling regardless of the total.

### Blast Radius
| Score | Condition |
|-------|-----------|
| 1 | One instance, or a non-customer-facing internal service |
| 3 | One customer-facing service, one region |
| 5 | Multiple services, shared infrastructure, or all regions |

### Reversibility
| Score | Condition |
|-------|-----------|
| 1 | Instant and verified — flag flip with a tested off-path |
| 3 | Reversible in minutes, documented procedure, exercised within 90 days |
| 5 | Irreversible, or a rollback that has never been exercised |

**Unknown reversibility scores 5.** Nobody being able to state the rollback is the strongest
available signal that there is not one.

### Coupling
| Score | Condition |
|-------|-----------|
| 1 | No dependents, no dependencies changing |
| 3 | Dependents tolerate the change (backwards-compatible contract) |
| 5 | Requires coordinated change across services or teams, with ordering constraints |

### Novelty
| Score | Condition |
|-------|-----------|
| 1 | Routine; done dozens of times on this system |
| 3 | Uncommon path, or common elsewhere but new here |
| 5 | First execution ever, or first on this system under this configuration |

### Batch Size
| Score | Condition |
|-------|-----------|
| 1 | One logical change |
| 3 | 2–5 logical changes |
| 5 | More than 5, or unknown (a release accumulated over weeks) |

## Totals

| Total | Handling |
|-------|----------|
| 5–9 | `Standard` **candidate** — grant the class only if it is also pre-approved, runbooked, and previously executed unchanged; a low score alone is not sufficient. Otherwise `Normal` |
| 10–15 | `Normal`; service owner approval; staged rollout |
| 16–20 | Elevated; explicit rollout plan, named watcher, coverage confirmed with `operation-oncall` |
| 21–25 | High; **split it**. If it cannot be split, sequence the phases and treat each as elevated |

## Batch Size Deserves Special Attention

Batch size is the dimension teams control most directly and reason about least.

- Change failure rate rises **super-linearly** with batch size: correlated risks compound.
- Diagnosis time rises with batch size: with one change, the trigger is known; with fifteen,
  bisection is required under pressure.
- Rollback granularity collapses: an urgent fix batched with unrelated work cannot be rolled
  back independently, so rolling back the failure also reverts everything else.

**When a change scores >20, the first recommendation is almost always "ship it in pieces",**
not "add more approval". More process on a large batch slows delivery without reducing risk.

Unsplittable cases are real (an atomic protocol change, a coordinated schema cutover) — say so,
and sequence the phases explicitly.

## Coupling and Sequencing

For multi-service changes, produce the ordering explicitly:

1. **Consumers tolerate first.** Deploy consumers that accept both old and new formats.
2. **Producers emit second.** Only after all consumers tolerate.
3. **Old format retired last**, as a separate change, after confirming no traffic uses it.

Reversing this order — producers first — breaks consumers immediately and gives a rollback
window measured in seconds.

Check for **collisions**: other in-flight changes to the same service, its dependencies, or
shared infrastructure. Two independently safe changes shipping simultaneously produce a state
neither team designed, and a diagnosis nobody can bisect.

## Novelty and the First Execution

The first execution of any procedure carries risk unrelated to the change's content: the
procedure itself is unverified.

- First-time changes get an extra rollout stage and a longer bake.
- First-time changes are never combined with other changes.
- First-time changes are never scheduled immediately before thin coverage — Friday afternoon,
  a holiday, or the start of a freeze.
- The person executing it for the first time has someone available who has done it elsewhere,
  or the procedure has been rehearsed non-production.

## Timing

| Window | Verdict |
|--------|---------|
| Business hours, full coverage | Preferred for anything above `Standard` |
| Off-hours for low-traffic reasons | Only when the failure mode is traffic-dependent **and** coverage is arranged |
| Friday afternoon | Only `Standard`, or genuinely urgent — otherwise the failure surfaces with nobody watching |
| Immediately before a freeze | Avoid; there is no room to iterate on the fix |
| Immediately after a freeze exit | Elevated — see freeze-exit risk concentration |
| During a declared incident | `Emergency` class only |

"Deploy at low traffic" is a weak argument when the failure mode is not load-related — it trades
full observability and staffed coverage for a smaller sample of affected users.
