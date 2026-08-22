<!-- operation:guidance -->
# Change Record, Risk Scoring

## Change Record

Every change assessed emits this. Incidents read it first when looking for a trigger.

```yaml
change: "<what is shipping, one line>"
class: Standard | Normal | Emergency
tier: T1 | T2 | T3 | T4
risk_score: <n>/25
services: [<affected>]
batch: "<number of logically distinct changes in this deploy>"
migration:
  present: yes | no
  phase: expand | migrate | contract | none
  reversible: yes | no | conditional
point_of_no_return: "<the moment after which rollback is unavailable, or NONE>"
rollback:
  procedure: "<runbook link or command>"
  last_exercised: <YYYY-MM-DD> | NEVER
  duration: "<expected>"
rollout:
  strategy: canary | blue-green | rolling | flag | shadow | direct
  stages: "<e.g. 1% -> 10% -> 50% -> 100%>"
  abort_trigger: "<metric, threshold, window>"
watcher: "<named individual>"
window: "<when>"
verdict: GO | GO WITH CONDITIONS | NO-GO
conditions: [<what must be true>]
```

## Risk Scoring

Score each dimension 1–5; the total orders the queue, and any single 5 forces `T3`+ handling.
The table anchors 1, 3, and 5. **2 and 4 are the interpolations** — use 4 when the case is
closer to the 5 anchor than the 3, and 2 likewise. When a score sits on a boundary that changes
the handling band, round **up** and say that you did.

| Dimension | 1 | 3 | 5 |
|-----------|---|---|---|
| **Blast radius** | One instance, one non-critical service | One customer-facing service | Multiple services, or shared infrastructure |
| **Reversibility** | Instant, verified | Reversible in minutes, procedure exists | Irreversible, or rollback never exercised |
| **Coupling** | No dependents | Dependents tolerate the change | Requires coordinated multi-service change |
| **Novelty** | Routine, done many times | Uncommon path | First time, or first time on this system |
| **Batch size** | One logical change | 2–5 | >5, or unknown |

| Total | Handling |
|-------|----------|
| 5–9 | `Standard` **candidate** — only if it also meets the class definition (pre-approved, runbooked, executed unchanged before). Otherwise `Normal` |
| 10–15 | Normal change; service owner approval; staged rollout |
| 16–20 | Elevated; explicit rollout plan, named watcher, coverage confirmed |
| 21–25 | High; split it. If it cannot be split, treat every phase as elevated and sequence them |

**A total above 20 is usually a batching problem, not an inherent one.** Recommend splitting
before recommending more process.
