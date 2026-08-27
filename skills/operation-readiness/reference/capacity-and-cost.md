<!-- operation:deferred -->
# Capacity and Cost

Purpose: Headroom, growth modelling, saturation ceilings, unit economics, cost as operational risk.
Read when: headroom, growth modelling, saturation ceilings, unit economics, cost as operational risk
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## Headroom

Headroom is a multiple of **current peak**, not of average, and it is meaningless without the
constraint that binds first.

| Tier | Required headroom | Verification |
|------|-------------------|--------------|
| T0 | ≥3× current peak | Load tested to saturation, with the saturating resource named |
| T1 | ≥2× | Load tested |
| T2 | ≥1.5× | Estimated with a stated method |
| T3 | None | — |

**Name the next ceiling with its value.** "It scales" is not an answer. "Tested to 4× current
peak; the database connection pool saturates at 4.2×" is.

**The tier multiples are a floor, not the requirement.** Derive the actual headroom the service
needs and take whichever is larger:

```
required = peak
         × failover_concentration   # if a region fails, survivors absorb its share
         × burst_factor             # peak-of-peak: launches, campaigns, retry storms
         × autoscale_lead_margin    # what must be absorbed before new capacity is ready
         × growth_to_next_review    # projected growth until the next capacity review
```

A service behind a two-region active/active with 10-minute autoscaling lead needs more than
`2×` even at T1. Where the derived figure is below the tier floor, the floor wins.

## Finding the Real Constraint

Headroom against requests per second is misleading whenever the binding constraint is something
else. Candidates:

| Constraint | Symptom at saturation |
|------------|----------------------|
| Database connection pool | Request queueing, timeouts under load, sudden cliff |
| Thread pool / worker count | Latency rises while CPU stays low |
| Per-account or per-partner rate limits | Errors concentrated on one tenant |
| Single-threaded consumer | Queue lag grows linearly and never recovers |
| Cloud account quotas | Scaling fails at a number nobody remembers setting |
| Third-party API limits | Failures appear only above a traffic threshold |
| Disk IOPS or throughput | Latency rises with no CPU or memory signal |
| Network bandwidth / connection tracking | Packet loss, connection resets |
| Certificate or licence limits | Hard, dated failure |
| Autoscaling maximum | Scaling stops silently, at the configured max |

Load testing that stops before saturation does not find the constraint. **Test to failure** in a
non-production environment, and record which resource failed and at what value.

## Growth Modelling

- Project from measured growth, not from a business plan.
- Model **peak** growth, not average — peak-to-average ratio often grows on its own.
- Include known step changes: product launches, marketing campaigns, partner onboarding,
  seasonal peaks, and the annual event everyone forgets until the week before.
- State the date when headroom drops below the tier's requirement. That date is the deadline
  for the next capacity action, and it is the output that matters.

```
Current peak:      <value> at <date>
Growth rate:       <%/month, from <window> of data>
Next ceiling:      <resource> at <value>
Headroom today:    <multiple>
Below tier minimum on: <date>
Action required by:    <date minus lead time>
```

## Saturation Behaviour

More important than the ceiling's value is what happens when it is reached.

| Behaviour | Assessment |
|-----------|------------|
| Graceful degradation — shed load, serve stale, queue | Good; verify the shed policy is deliberate about *whose* traffic is dropped |
| Uniform slowdown | Poor — everything gets slow, nothing works, the failure is hard to diagnose |
| Cascading failure | Dangerous — timeouts propagate, retries amplify, recovery requires a coordinated restart |
| Silent data loss | Unacceptable at any tier — writes accepted and discarded is the worst failure mode |
| Hard stop with clear errors | Acceptable; users get a definite answer |

Test saturation behaviour deliberately. A system that has never been pushed past its limit has
undefined behaviour there, and it will be discovered during peak.

## Cost as Operational Risk

Cost is not only a finance concern — it constrains operations.

- **Cost per unit** (per request, per user, per transaction) with its trend. Rising unit cost
  means the service becomes less viable as it succeeds.
- **Cost of headroom** — the tier's requirement has a price; state it so the tier decision is honest.
- **Cost-driven risk**: a service whose cost scales faster than its revenue will be limited by
  budget before it is limited by technology, and that limit arrives without a warning graph.
- **Incident cost**: what does an hour of degraded operation cost in extra compute, from
  retries, autoscaling, and reprocessing? Some failure modes are expensive even when mitigated.

| Cost signal | Operational meaning |
|-------------|--------------------|
| Unit cost rising with scale | Negative economies of scale; a growth ceiling is approaching |
| Cost spike with no traffic change | Retry storms, a runaway job, or a misconfiguration — investigate as an incident |
| Large share in one resource | A single point of both cost and failure |
| Autoscaling max set for cost reasons | A capacity ceiling nobody documented as one |
| Reserved capacity expiring | A scheduled cost cliff |

## Waste

Identify, but do not act unilaterally — idle capacity is sometimes deliberate headroom:

- Over-provisioned instances relative to measured peak
- Orphaned resources: unattached volumes, idle load balancers, unused environments
- Retention longer than the policy requires
- Non-production environments running outside working hours
- Data transfer patterns that cross zones or regions unnecessarily
- Duplicate storage of the same data across systems

Always ask what the resource protects before recommending its removal. Cost reduction that
removes headroom converts a budget saving into a capacity incident.
