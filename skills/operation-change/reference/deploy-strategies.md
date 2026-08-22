<!-- operation:deferred -->
# Deploy Strategies

Purpose: Choosing canary / blue-green / rolling / flag / shadow, stage design, bake times, abort triggers.
Read when: choosing canary / blue-green / rolling / flag / shadow, stage design, bake times, abort triggers
Verified: 2026-08-21 — no automated check.

## Selection

| Strategy | Rollback speed | Blast radius during rollout | Cost | Best for |
|----------|---------------|----------------------------|------|----------|
| **Direct** | Full redeploy | 100% immediately | None | `Standard`, low-risk, non-customer-facing |
| **Rolling** | Partial, slow | Grows with each batch | None | Stateless services, backwards-compatible changes |
| **Blue-green** | Instant (switch back) | 0% until cutover, then 100% | 2× capacity | Fast rollback matters more than gradual exposure |
| **Canary** | Fast (stop and shift back) | Bounded by canary share | Routing complexity | Customer-facing changes with measurable SLIs |
| **Feature flag** | Instant for the code path; side effects persist | Bounded by flag targeting | Flag debt | Behaviour changes decoupled from deploy |
| **Shadow / mirror** | N/A (no user traffic) | 0% | 2× compute on mirrored path | Validating a rewrite or a new dependency under real traffic |

**Blue-green gives fast rollback but not gradual exposure** — at cutover, 100% of users hit the
new version at once. Combine with canary when both properties are wanted.

**Feature flags decouple deploy from release**, which is their real value: the code ships dark,
and the behaviour change is a separate, instantly reversible action.

**But flipping a flag off does not undo what it did while it was on.** Records written in the
new shape, messages published, emails sent, charges taken, and caches filled all persist. A flag
is instantly reversible in *behaviour*, not in *side effects* — enumerate them exactly as you
would for a deploy. A flag guarding a write path has a point of no return like anything else.

## Canary Stages

| Stage | Population | Bake time | Promote when | Abort when |
|-------|-----------|-----------|--------------|------------|
| 1 | 1% | ≥ slowest feedback loop | Error rate and latency within tolerance of baseline | Any abort trigger fires |
| 2 | 10% | ≥ 15 min | Same, with statistically meaningful volume | Same |
| 3 | 50% | ≥ 30 min | Same, plus downstream systems healthy | Same |
| 4 | 100% | ≥ 30 min monitoring | All SLIs at baseline, backlogs drained | Rollback |

**Promotion is gated on metrics, with time as a floor, never on time alone.** A timer-based
promotion ships a broken canary on schedule.

## Bake Time

Bake time must exceed the **slowest feedback loop that could reveal the failure**:

| Feedback mechanism | Minimum bake |
|--------------------|--------------|
| Synchronous request errors | 5 min |
| Latency percentile shift | 15 min |
| Async job / queue processing | 1 job cycle + 15 min |
| Hourly batch job | 1 full cycle |
| Nightly reconciliation | Not coverable by bake — needs a flag and a next-day check |
| Memory leak / resource exhaustion | Hours to days — needs a longer canary hold, not a longer bake |
| Cache-dependent behaviour | Cache TTL + 15 min |

State the chosen bake time **and the feedback loop it is derived from**. A bake time with no
stated rationale is a number someone felt comfortable with.

## Canary Population Selection

The most common canary defect: a population that does not exercise the risk.

| Selection | Covers | Misses |
|-----------|--------|--------|
| Random hash of user id | Typical traffic | Rare payloads, largest customers, edge regions |
| Internal users first | Fast feedback, low blast radius | Real customer data shapes and scale |
| One region | Regional infrastructure differences | Cross-region behaviour |
| Low-value traffic tier | Protects revenue | The high-value path that actually matters |
| Specific opt-in customers | Real usage, willing participants | Representativeness |

Always state what the canary **does not** cover. A canary that never sees enterprise-scale
payloads gives no evidence about them, and the promotion decision should say so.

## Abort Triggers

Defined **numerically, before the rollout starts**. During a rollout, everyone finds reasons to
continue; the number decides instead.

```yaml
abort_triggers:
  - metric: "error_rate(canary) - error_rate(baseline)"
    threshold: "> 0.5 percentage points"
    window: "5m"
  - metric: "latency_p99(canary) / latency_p99(baseline)"
    threshold: "> 1.2"
    window: "10m"
  - metric: "any SEV1 or SEV2 declared on this service"
    threshold: "any"
    window: "immediate"
  - metric: "downstream_error_rate(any dependent)"
    threshold: "> baseline + 1pp"
    window: "10m"
```

**Compare canary to concurrent baseline, not to yesterday.** Traffic patterns, dependency
health, and load all shift; a canary compared to a historical baseline produces both false
alarms and false confidence.

Abort is **automatic where the tooling allows it** — a human deciding whether the threshold was
"really" crossed defeats the purpose.

The exception is the abort *action* itself: automatic abort is safe while the reversal is `T2`
(stop the rollout, shift traffic back, flip the flag). Once the rollout has passed a point of no
return, or the only remaining reversal is `T3`+, automatic abort must **stop and page** rather
than execute — an automated `T4` reversal is exactly what `_operation/SAFETY_TIERS.md` forbids.
State per stage which kind of abort applies.

## Watcher

Every rollout above `Standard` names a watcher — a person, not a dashboard. The watcher:

- Is not the person executing the rollout (execution absorbs attention)
- Knows the abort triggers and has the authority to abort without consulting anyone
- Is present for the full bake time, including the final stage
- Confirms the user-path check at the end, not just the metrics

"The team is watching" means nobody is.

## Shadow Traffic

For validating rewrites and new dependencies:

- Mirror real requests to the new path; discard the responses.
- Compare responses offline for correctness — this is the point, and it is often skipped.
- **Watch for side effects.** A shadow path that writes to the same database is not shadow
  traffic; it is a second production writer. Verify write isolation before mirroring.
- Account for the load: mirroring doubles the traffic to shared downstream dependencies.
