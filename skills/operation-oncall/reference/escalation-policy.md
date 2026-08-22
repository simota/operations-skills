<!-- operation:deferred -->
# Escalation Policy

Purpose: Designing escalation tiers, timeouts, unacknowledged-page fallback, severity-to-channel routing.
Read when: designing escalation tiers, timeouts, unacknowledged-page fallback, severity-to-channel routing
Verified: 2026-08-21 — no automated check.

## Tier Structure

| Tier | Target | Trigger | Timeout to next |
|------|--------|---------|-----------------|
| 0 | Automated remediation | Alert fires, pattern is known | 5 min (or on failure) |
| 1 | Primary on-call | Automation absent or failed | 5 min unacknowledged |
| 2 | Secondary on-call | Primary unacknowledged, or primary requests help | 5 min unacknowledged |
| 3 | Service owner / team lead | Tier 2 unacknowledged, or scope exceeds on-call authority | 10 min |
| 4 | Engineering manager + IC pool | Tier 3 unacknowledged, or SEV1 declared | 10 min |
| 5 | Executive / customer-facing leadership | SEV1 past the communication threshold, or regulatory exposure | — |

Timeouts are for **unacknowledged** pages. A responder who acknowledges and is working stops
the timer — but see "Acknowledged Is Not Handled" below.

## Total Escalation Budget

From alert fire to a human definitely engaged: **≤15 minutes**. If the chain from Tier 1 to
Tier 3 cannot complete inside that, the timeouts are too long. Work backwards from 15 minutes,
not forwards from what feels polite.

## Fallback When the Chain Fails

The most common design gap: what happens when *nobody* acknowledges at any tier.

Required fallback behaviour, in order:

1. Re-page all tiers simultaneously (broadcast, not sequential).
2. Notify the team channel with an explicit "no acknowledgement after N minutes" message.
3. Page the designated **last-resort** contact — a named individual, on a channel they cannot
   mute (phone call, not push notification).
4. Log a control failure. Every full-chain miss is reviewed, regardless of outcome.

A policy whose last step is "post to Slack" has no fallback.

## Acknowledged Is Not Handled

Acknowledgement stops escalation, which makes it a silent failure mode: a responder who
acknowledges from a phone and falls back asleep has disabled the safety net.

Countermeasures:

- **Re-escalate on stalled progress**: if no status update within 15 minutes of acknowledgement
  on a SEV1/SEV2, resume escalation automatically.
- Require an explicit `taking-it` action distinct from `ack`, where the tooling supports it.
- Track time-to-first-diagnostic-action alongside MTTA (see `oncall-health.md`).

## Severity-to-Channel Routing

| Severity | Channel | Hours | Acknowledgement SLA |
|----------|---------|-------|--------------------|
| SEV1 | Phone call + push + broadcast to team | 24/7 | 5 min |
| SEV2 | Push notification | 24/7 | 15 min |
| SEV3 | Ticket + team channel | Business hours | Next business day |
| SEV4 | Ticket queue | Business hours | Next sprint |

**Only SEV1/SEV2 may page.** SEV3 arriving as a page is a routing defect, and it is how
responders learn to treat pages as background noise.

**Precedence when this table and the service tier disagree**: the table above is the routing for
T0 and T1. For T2 and T3, the tier's off-hours degradation (below) wins — a SEV2 on a T2 service
becomes a business-hours ticket. **A SEV1 always pages, at every tier**; if a T3 service can
produce a genuine SEV1, its tier is wrong.

## Escalation Authority

Escalation is a **right, not a failure**. The policy must state explicitly:

- Any responder may escalate at any time, for any reason, without justifying it first.
- Escalating early is never penalised. Not escalating is.
- The responder decides they are stuck; nobody else gets to decide they should have coped.

Write this into the policy document verbatim. Teams that leave it implicit produce responders
who burn 40 minutes avoiding the appearance of incompetence.

## Business-Hours Degradation

For services whose tier permits it, escalation differs by time of day. State it as a table,
never as an unwritten norm:

| Service tier | Off-hours behaviour |
|--------------|--------------------|
| T0 | Full chain, 24/7, no degradation |
| T1 | Full chain 24/7; Tier 4+ business hours only |
| T2 | Page for SEV1 only; SEV2 becomes a business-hours ticket |
| T3 | No off-hours paging; SEV2–4 queue to business hours. A genuine SEV1 still pages — and triggers a tier review, because a T3 service should not be able to produce one |

Service tiers are defined by `operation-readiness`.

## Common Defects

- **Sequential-only escalation with long timeouts** — 15 minutes per tier means 45 minutes to
  reach a service owner on a SEV1.
- **Escalation target is a rotation with the same people** — Tier 2 pointing at a schedule
  where primary is also secondary.
- **Group inbox as an escalation target** — diffuse ownership means no acknowledgement.
- **No holiday-aware routing** — Tier 3 is on annual leave and the chain silently terminates.
- **Untested chain** — run a deliberate no-acknowledge test quarterly. An escalation path
  that has never fired is a hypothesis.
