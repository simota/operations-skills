<!-- operation:guidance -->
# Change Record, Risk Scoring

## Change Record

Every change assessed emits this. Incidents read it first when looking for a trigger.

```yaml
change: "<what is shipping, one line>"
class: Standard | Normal | Emergency
safety_tier: T1 | T2 | T3 | T4
service_tier: ST0 | ST1 | ST2 | ST3   # as operation-readiness assigned it
risk_score: <n>/25
deciding_dimension: "<the dimension that set the handling, and its score>"
services: [<affected>]
batch: "<number of logically distinct changes in this deploy>"
migration:
  present: yes | no
  phase: expand | migrate | contract | none
  reversible: yes | no | conditional
point_of_no_return: "<the moment after which rollback is unavailable, or NONE>"
rollback:
  procedure: "<runbook link or command>"
  state: proved | simulated | stale | untested | unprovable
  proved_on: <YYYY-MM-DD> | NEVER
  expires: "<YYYY-MM-DD> or on any change to <named surface>"
  duration: "<expected>"
rollout:
  strategy: canary | blue-green | rolling | flag | shadow | direct
  stages: "<e.g. 1% -> 10% -> 50% -> 100%>"
  abort_trigger: "<metric, threshold, window>"
watcher: "<named individual>"
approvers: ["<named individual>"]   # per class, risk band, safety tier; two from the 16–20 band up (total ≥16 or any 5), or at T4
window: "<when>"
not_tested: "<what was not tested, or NONE>"
verdict: GO | GO-WITH-CONDITIONS | NO-GO
conditions: [<what must be true>]
```

## Risk Scoring

Score each dimension 1–5; the total orders the queue, and any single 5 takes at least the 16–20
approval band. The score never sets the safety tier — except that a Reversibility 5 is `T4`: an
irreversible action by the tier table, an undo that never ran by rule 2 (`_operation/SAFETY_TIERS.md`;
`stale` counts as `untested`, per `_operation/EXPIRY.md`).
The table anchors 1, 3, and 5. **2 and 4 are the interpolations** — use 4 when the case is
closer to the 5 anchor than the 3, and 2 likewise. When a score sits on a boundary that changes
the handling band, round **up** and say that you did.

| Dimension | 1 | 3 | 5 |
|-----------|---|---|---|
| **Blast radius** | One instance, or a non-customer-facing internal service | One customer-facing service, one region | Multiple services, shared infrastructure, or all regions |
| **Reversibility** | Instant, verified | Reversible in minutes, procedure `proved` and unexpired, or `simulated` end to end in a lower environment, gap stated | Irreversible, or rollback `untested`, `stale`, `unprovable`, or `simulated` with its undo stubbed or its gap unstated |
| **Coupling** | No dependents | Dependents tolerate the change | Requires coordinated multi-service change |
| **Novelty** | Routine, done many times | Uncommon path | First time, or first time on this system |
| **Batch size** | One logical change | 2–5 | >5, or unknown |

| Total | Handling |
|-------|----------|
| 5–9 | `Standard` **candidate** — only if it also meets the class definition (pre-approved, runbooked, executed unchanged before). Otherwise `Normal` |
| 10–15 | Normal change; service owner approval; staged rollout, named watcher |
| 16–20 | Elevated; explicit rollout plan, named watcher, coverage confirmed |
| 21–25 | High; split it. If it cannot be split, treat every phase as elevated and sequence them |

**A total above 20 is usually a batching problem, not an inherent one.** Recommend splitting
before recommending more process.
