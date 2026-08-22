<!-- operation:deferred -->
# Severity Matrix

Purpose: Classifying severity, declaration criteria, upgrade/downgrade rules, concurrent incidents.
Read when: classifying severity, declaration criteria, upgrade/downgrade rules, concurrent incidents
Verified: 2026-08-21 — no automated check.

## Classification

Severity is the **maximum** across all dimensions, not the average. One SEV1 dimension makes
it a SEV1.

**The dimensions are scaled, not binary.** A single corrupted record that is detectable and
recoverable is not the same event as unbounded corruption, and the table says so — read the
qualifiers, not just the noun. Where scope is genuinely unknown, rule 1 of scoping applies:
assume the worst plausible case, declare at that level, and correct as evidence arrives.
Correcting downward is free; that is the point of declaring early.

| Dimension | SEV1 | SEV2 | SEV3 | SEV4 |
|-----------|------|------|------|------|
| **Users affected** | All users, or all of a region/tier | Large subset (>10%) or all of one major feature | Small subset (<10%), workaround exists | Individual users, cosmetic |
| **Functionality** | Core workflow unusable | Core workflow degraded, or secondary unusable | Secondary degraded | Cosmetic or non-functional |
| **Data** | Unbounded or unrecoverable loss/corruption, or exposure to an unauthorised party | Bounded and recoverable loss/corruption; integrity at risk | Staleness beyond the freshness SLO | Reporting-only discrepancy |
| **Revenue** | Transactions failing broadly, or unbounded value at risk | Transactions degraded or delayed, or a bounded subset failing | Non-transactional impact | None |
| **Regulatory** | Notification clock has started | Potential exposure under assessment | Control gap, no exposure | None |
| **Reputation** | Public/press/social visibility | Multiple customers escalating | Single customer escalating | Internal only |

## Response Expectations

| Severity | Ack | IC required | Scribe | Comms cadence | Postmortem |
|----------|-----|-------------|--------|---------------|------------|
| SEV1 | 5 min | Yes, dedicated | Yes | 30 min, no exceptions | Mandatory, within 5 business days |
| SEV2 | 15 min | Yes (may also be OL if pool is thin) | Yes | 60 min | Mandatory, within 10 business days |
| SEV3 | Next business hour | No | No | On state change | If repeated ≥3× in 90 days |
| SEV4 | Next business day | No | No | On resolution | No |

The comms cadence holds **even when there is nothing new**. "No change, still investigating,
next update at HH:MM" is a valid and necessary update — silence is read as abandonment.

## Upgrade and Downgrade

**Upgrade immediately when:**
- Impact expands to another dimension at a higher level.
- Mitigation attempt fails and no alternative is ready.
- Duration exceeds the severity's expectation (SEV2 past 2 hours → reassess as SEV1).
- Data integrity moves from "unaffected" to "unknown". Unknown is not "fine".
- A second incident starts and shares the responder pool.

**Downgrade when** impact is genuinely reduced — mitigation is verified from the user's
perspective and holding. Downgrading requires the IC's explicit call and a comms update; a
severity that quietly decays produces stakeholders who think it is still SEV1 for days.

Record every severity change with a timestamp and the deciding dimension. Postmortems reliably
ask "why was this a SEV2 for the first hour?"

## Concurrent Incidents

Severity is per-incident, but **capacity is shared**. Two SEV2s against one responder pool is
operationally SEV1: assess aggregate impact and escalate for additional responders, not for
additional severity labels.

Rules:
- One IC may command at most one active incident. A second incident needs a second IC.
- If no second IC is available, that fact is itself escalated — it is a coverage failure.
- Communications for concurrent incidents stay separate. Merging them hides which one is
  affecting a given customer.

## Declaration Criteria

Declare when **any** holds:

- A user-facing SLO burns fast enough to exhaust the budget in <24h.
- A customer report reproduces.
- Data integrity, durability, or confidentiality is in question.
- The responder does not understand what is happening and impact is plausible.
- Two or more teams are needed.
- Someone asks "should we declare?"

**False declarations are free and are never penalised.** State this in the incident record
template so the next responder reads it at the moment of hesitation.

## Anti-patterns

- **Severity inflation to get attention.** If SEV1 is the only way to get responders, the
  escalation policy is broken — fix that, not the label.
- **Severity deflation to avoid a postmortem.** Detectable: a cluster of 2h+ SEV3s. Any SEV3
  exceeding its expected duration is reassessed automatically.
- **Waiting for confirmation before declaring.** Declaration is how you get the people who
  can confirm.
- **Severity set by seniority.** The person with the most context sets it; the IC owns the
  final call, not the most senior person in the room.
- **"Unknown impact" recorded as low severity.** Unknown scope defaults to the highest
  plausible level until scoped, then is corrected.
