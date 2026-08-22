<!-- operation:deferred -->
# Rotation Design

Purpose: Sizing a responder pool, choosing shift shape, follow-the-sun trade-offs, fairness accounting, coverage-gap detection.
Read when: sizing a responder pool, choosing shift shape, follow-the-sun trade-offs, fairness accounting, coverage-gap detection
Verified: 2026-08-21 — no automated check.

## Pool Sizing

The binding constraint is not headcount — it is the per-person night burden.

| Pool size | 24/7 primary cadence | Night burden | Verdict |
|-----------|---------------------|--------------|---------|
| 1 | Always | Every night | Not a rotation. Single point of failure. |
| 2 | 1 week in 2 | Every other week | Unsustainable beyond ~1 month |
| 3–4 | 1 week in 3–4 | 1 in 3–4 | Below minimum — degraded options only |
| 5 | 1 week in 5 | 1 in 5 | Below minimum — state the deficit, offer degraded options |
| 6–8 | 1 week in 6–8 | 1 in 6–8 | Minimum sustainable |
| >10 | 1 week in 10+ | rare | Healthy, but skill decay — see below |

**Skill decay above 10.** When a responder carries the pager once a quarter, they arrive
cold. Compensate with shadow shifts, game days, or split the rotation by domain rather than
diluting one rotation across everyone.

**Six is the floor for 24/7 primary coverage** (`operation-oncall/SKILL.md` Core Contract).
Below it, never present a schedule as if it were sustainable — name the deficit first.

### Degraded Options When the Pool Is Too Small

Never silently schedule an unsustainable rotation. Offer explicitly:

1. **Business-hours-only coverage** with an accepted, documented overnight recovery time.
   Requires the service tier to permit it — check `operation-readiness`.
2. **Shared rotation** with an adjacent team. Requires that team to be able to act, which
   means runbooks first.
3. **Reduce the paging surface** until the load fits the pool. Usually the right answer.
4. **Vendor or managed-service coverage** for the tier-appropriate subset.
5. **Hire.** State the number, not "more people".

## Shift Shapes

| Shape | Period | Best for | Cost |
|-------|--------|----------|------|
| Weekly | Mon 10:00 → Mon 10:00 | Low page volume, context continuity | One bad week ruins a week |
| Split week | Mon–Thu / Fri–Sun | Protecting weekends unevenly is worse; splitting shares them | Two handoffs per week |
| Daily | 24h | High page volume | Context loss; heavy handoff cost |
| Day/night split | 12h × 2 | Sustained night load with a large pool | Doubles pool requirement |
| Follow-the-sun | 8–12h per region | Genuinely global teams, irreducible night load | Handoff boundary, coordination overhead |

**Handoff time matters.** Start shifts mid-morning (e.g. 10:00), never at 00:00 or on a
Monday 09:00 boundary. A shift starting at midnight begins with a tired handoff; one starting
at the top of Monday collides with the week's first deploys.

## Follow-the-Sun

Only justified when night load is irreducible *after* alert triage. Requirements:

- Each region must be able to act independently — full runbook parity, not "escalate to APAC".
- A structured handoff at each boundary (`reference/shift-handoff.md`). Three handoffs a day
  is three chances to drop context.
- Shared incident tooling and a single timeline of record.
- Aligned severity definitions. Regions with different SEV1 thresholds produce inconsistent
  customer communication.

Anti-pattern: **the sundial rotation** — one region carries the pager 24/7 while others hold
business-hours-only, labelled follow-the-sun. Name it for what it is.

## Secondary Position

Secondary exists for three specific cases:

1. Primary does not acknowledge within the escalation timeout.
2. Primary needs a second pair of hands on a live incident.
3. A second concurrent incident.

It is **not** for routine consultation — that trains primary to escalate rather than act.

Secondary must be a *different person from a different sub-domain* where possible; two
responders with the same blind spot provide one perspective, not two.

## Fairness Accounting

Track and publish, per responder, per quarter:

| Dimension | Why it matters |
|-----------|----------------|
| Total shifts | Baseline equity |
| Weekend shifts | Weekends cost more than weekdays |
| Public holiday shifts | Highest cost; rotate deliberately |
| Pages received | Two people on "the same" rotation can carry 5× the load |
| Off-hours pages | The real burden metric |
| Shift swaps given vs. received | Chronic givers are absorbing hidden load |

Equal shift *counts* with unequal *page* counts is not fairness. Publish both.

## Coverage Gaps to Check

- Handoff boundaries — is anyone paged during the transition minute?
- Public holidays, per responder's country, not the company's headquarters.
- Company-wide events (all-hands, offsites, retro days).
- Deploy freeze exits — first day back typically concentrates change risk.
- Simultaneous vacation of primary and secondary.
- The responder who is also the only escalation target for another rotation.

## Compensation Models

Employment terms — always `Ask First`. Common shapes, stated neutrally:

| Model | Notes |
|-------|-------|
| Flat stipend per shift | Simple; decouples pay from actual load, so noisy rotations stay unfixed |
| Stipend + per-page payment | Aligns cost with noise, creating pressure to fix alerts |
| Time off in lieu | Preserves recovery; requires slack in the team to honour |
| Included in salary band | Common at senior levels; hides the cost entirely — worst for surfacing noise |

Whatever the model, the load must still be measured. Compensation is not a substitute for
reducing pages.
