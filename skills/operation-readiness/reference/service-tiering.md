<!-- operation:deferred -->
# Service Tiering

Purpose: Assigning ST0–ST3, deriving requirements, dependency tier inversion.
Read when: assigning ST0–ST3, deriving requirements, dependency tier inversion
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

Tier is derived from **measured impact of downtime**, never from how important the service
feels to the team that built it.

One hour is the default probe because it is comparable across services. It is the wrong probe
for **deadline-shaped** workloads — a monthly settlement job, a regulatory filing, a payroll
run — where an hour of downtime costs nothing on most days and everything on one. For those,
tier on the **impact of missing the deadline**, and record the window in which the service is
effectively ST0 even if it is ST3 the rest of the month.

## Tier Definitions

| Tier | Downtime impact in one hour | Examples |
|------|----------------------------|----------|
| `ST0` | Revenue stops, regulatory exposure, or safety impact | Payment processing, authentication, order capture |
| `ST1` | Major feature unusable; customers notice and escalate | Search, notifications, primary API |
| `ST2` | Degraded experience with a workaround; internal disruption | Reporting, admin tooling, secondary features |
| `ST3` | Barely noticed within a business day | Internal dashboards, batch analytics, dev tooling |

## Deriving the Tier

Answer with numbers, not adjectives:

- How much revenue is not collected during one hour of downtime — and is there a date or window where that figure is far higher?
- How many users are blocked from their primary task?
- Does any regulatory or contractual notification clock start?
- Does data become unrecoverable, or does a backlog become unrecoverable?
- Which other services stop working? (Tier is at least that of anything depending on it.)
- Can the business operate manually for an hour? For a day?

If nobody can answer these, that inability is a finding — a service whose downtime cost is
unknown cannot be tiered, staffed, or funded correctly.

## Requirements by Tier

The requirement matrix is canonical in `playbooks/verdict.md` § Tier Requirements —
it is read whenever a verdict is issued, so it is not duplicated here. This file covers derivation, dependency
inversion, cost, and review.

## Dependency Tier Inversion

**A service cannot be more available than its least available dependency.** A dependency
tiered below the service is a blocking finding at ST0, ST1, and ST2.

Dependencies teams routinely omit from the list:

- Authentication and authorisation services
- Configuration stores and feature flag providers
- Service discovery and DNS
- Secret managers and certificate issuance
- Message brokers and queues
- Shared databases, caches, and object storage
- The CI/CD system — because it is how the fix ships during an incident
- Observability — because without it, response is blind
- The paging provider itself
- Third-party APIs, including their own status commitments

Map the full dependency graph, tier each node, and flag every inversion. Remediation options:
raise the dependency's tier, remove the dependency, or degrade gracefully when it is absent —
graceful degradation being the only one that does not require someone else's budget.

## Tier and Cost

Tier requirements cost money and human nights. State the cost when assigning:

- ST0 needs ≥6 people for 24/7 primary alone (`operation-oncall`'s floor), plus secondary depth —
  drawn from the same six, it puts each person on call two weeks in six, so size the pool for
  both — plus 3× capacity headroom.
- Tier inflation is expensive and self-defeating: when everything is ST0, nothing is prioritised
  during a multi-service incident.
- **Tier inflation is detectable**: if more than roughly a quarter of services are ST0, the
  tiering exercise has not been done — it has been negotiated.

## Reviewing Tiers

Reassess annually, and on:

- A change in business model or traffic mix
- A new dependency introduced
- A service becoming a dependency of a higher-tier service (automatic promotion)
- Repeat incidents suggesting the current tier's support is insufficient

**Lowering a tier is a dialogue first** (`_operation/SIZING.md`) — it removes support that people currently depend on, often
including a rotation that will be dissolved and hard to rebuild.
