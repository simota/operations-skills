<!-- operation:deferred -->
# Delivery Health

Purpose: DORA four keys, change failure rate attribution, batch-size analysis, constraint identification.
Read when: dORA four keys, change failure rate attribution, batch-size analysis, constraint identification
Source: DORA — the four keys and their definitions are theirs, not this page's.
Verified: 2026-08-21 — no automated check.

## The Four Keys

| Metric | Definition | Measured from |
|--------|------------|---------------|
| **Deployment frequency** | How often changes reach production | Deploy events, per service |
| **Lead time for change** | First commit of the change → running in production | VCS + deploy timestamps |
| **Change failure rate** | Deploys causing degraded service requiring remediation ÷ all deploys | Change records ↔ incidents |
| **Failed deployment recovery time** | Impact start → service restored, for change-caused impact | Incident records |

Measure **per service**, not per organisation. An aggregate across a monolith and forty
microservices describes nothing that exists.

## Definitional Traps

- **Change failure rate counts deploys that needed remediation**, including rollbacks, hotfixes,
  and flag reverts — not only declared incidents. Teams that count only incidents report a
  flattering and useless number.
- **Lead time starts at the first commit**, not at ticket creation — that is DORA's own
  definition, and it deliberately includes review and queueing, which are usually where the
  time goes. Measuring from merge instead is a common local variant that hides review latency;
  if a team does that, label it "merge-to-deploy" rather than calling it DORA lead time.
- **Recovery time is for change-caused impact only.** Mixing in all incidents measures
  operational maturity, not deployment safety.
- **Deployment frequency counts production deploys**, not CI runs or staging deploys.

## Batch Size — The Missing Fifth Metric

Report alongside the four keys. It explains most of the variance in the other four:

| Measure | Signal |
|---------|--------|
| Commits per deploy | Batch size proxy |
| Files changed per deploy | Blast radius proxy |
| Time between merge and deploy | Queueing; large values mean batching by delay |
| Changes per deploy (logical) | The number that predicts failure rate |

Large batches simultaneously worsen change failure rate (correlated risk), recovery time
(bisection under pressure), and lead time (queueing). A team improving batch size usually
improves all four keys without targeting them.

## Interpreting

Do not chase benchmark tiers. Read the **relationships**:

| Pattern | Interpretation |
|---------|----------------|
| Low frequency + low failure rate | Possibly healthy; possibly a freeze or heavy process suppressing volume. Check batch size |
| High frequency + high failure rate | Fast delivery without safety. Progressive rollout and verification are missing |
| Low frequency + high failure rate | Large batches. The primary fix is batch size, not more approval |
| High frequency + low failure rate + long recovery | Good prevention, weak mitigation. Invest in rollback and runbooks |
| Long lead time + short deploy time | The bottleneck is review or queueing, not deployment |
| Improving frequency, worsening recovery | Delivery is outpacing operational readiness |

## Change Failure Attribution

For every change-caused incident, record:

- The change class (`Standard` / `Normal` / `Emergency`)
- The risk score, and whether it was accurate in hindsight
- Batch size
- Whether a staged rollout was used, and whether the abort trigger fired
- Whether rollback was available, and whether it worked
- Time from deploy to detection

Cluster these quarterly. The pattern names the constraint:

| Cluster | Constraint |
|---------|-----------|
| Failures concentrated in large batches | Batch size |
| Failures detected late | Post-deploy verification, or missing SLI coverage |
| Rollbacks that did not work | Reversibility verification |
| Failures in changes scored low-risk | The risk model is miscalibrated — recalibrate the dimensions |
| Failures concentrated in `Emergency` changes | The normal path is too slow, so people route around it |

## Reporting

Monthly, per service:

- Four keys with 6-month trend
- Batch size distribution
- Change failure attribution clusters
- Emergency change share — high share means the normal path is being bypassed
- Rollback exercise dates for `T3`+ procedures — the number of them at `NEVER` is the most
  actionable line in the report

## Anti-patterns

- **Targeting the metrics directly.** Deployment frequency rises trivially by splitting one
  deploy into five; nothing improves. Target batch size and reversibility; the keys follow.
- **Organisation-wide aggregates.** They hide the one service dragging everything down and
  demoralise the teams already doing well.
- **Using the keys for individual or team comparison.** They measure the system, and using them
  for evaluation guarantees they will be gamed within a quarter.
- **Ignoring recovery time because failures are rare.** Compare on *expected impact* —
  frequency × duration — not on either alone. Rare-but-slow and frequent-but-fast can land in
  the same place; what makes rare-but-slow the more dangerous of the two is that the recovery
  path is unexercised and the team is out of practice, so the real duration exceeds the
  measured one.
