<!-- operation:deferred -->
# Escalation Policy

Purpose: Designing escalation levels, timeouts, unacknowledged-page fallback, severity-to-channel routing.
Read when: designing escalation levels, timeouts, unacknowledged-page fallback, severity-to-channel routing
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## Level Structure

| Level | Target | Trigger | Timeout to next |
|------|--------|---------|-----------------|
| 0 | Automated remediation | Alert fires, pattern is known | 2 min (or on failure) |
| 1 | Primary on-call | An alert that pages, with automation absent or failed | 5 min unacknowledged |
| 2 | Secondary on-call | Primary unacknowledged, or primary requests help | 3 min unacknowledged |
| 3 | Service owner / team lead | Level 2 unacknowledged, or scope exceeds on-call authority | 5 min |
| 4 | Engineering manager + IC pool | Level 3 unacknowledged, or SEV1 declared | 10 min |
| 5 | Executive / customer-facing leadership | The leadership notice falls due (`operation-incident` comms: SEV1, or SEV2 past 1h) — sent by the comms lead, not paged — or regulatory exposure | — |

Timeouts are for **unacknowledged** pages. A responder who acknowledges and is working stops
the timer — but see "Acknowledged Is Not Handled" below.

## Total Escalation Budget

From alert fire to a human definitely engaged: **≤15 minutes**. If the chain from Level 0 to a
Level 3 acknowledgement cannot complete inside that, the timeouts are too long — the defaults
above page Level 3 at 2 + 5 + 3 = 10 minutes, leaving it 5 to acknowledge. Work backwards from 15 minutes,
not forwards from what feels polite.

## Fallback When the Chain Fails

The most common design gap: what happens when *nobody* acknowledges at any level.

Required fallback behaviour, in order:

1. Re-page all levels simultaneously (broadcast, not sequential).
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
- Track time-to-first-diagnostic-action alongside MTTA (see `reference/oncall-health.md`).

## Severity-to-Channel Routing

| Severity | Channel | Hours | Acknowledgement SLA |
|----------|---------|-------|--------------------|
| SEV1 | Phone call + push + broadcast to team | 24/7 | 5 min |
| SEV2 | Push notification | 24/7 | 15 min |
| SEV3 | Ticket + team channel | Business hours | Next business hour |
| SEV4 | Ticket queue | Business hours | Next business day |

The acknowledgement SLA is the target reported per severity; the Level Structure timeouts still
govern escalation for every severity that pages, so an unacknowledged SEV2 reaches secondary
after 5 minutes, not 15.

**Only SEV1/SEV2 may page.** SEV3 arriving as a page is a routing defect, and it is how
responders learn to treat pages as background noise.

**Precedence when this table and the service tier disagree**: the table above is the routing for
ST0 and ST1. For ST2 and ST3, the service tier's off-hours degradation (below) wins — a SEV2 on an ST2 service
becomes a business-hours ticket. **A SEV1 always pages, at every service tier**; if an ST3 service can
produce a genuine SEV1, its service tier is wrong.

## Escalation Authority

Escalation is a **right, not a failure**. The policy must state explicitly:

- Any responder may escalate at any time, for any reason, without justifying it first.
- Escalating early is never penalised. Not escalating is.
- The responder decides they are stuck; nobody else gets to decide they should have coped.

Write this into the policy document verbatim. Teams that leave it implicit produce responders
who burn 40 minutes avoiding the appearance of incompetence.

## Business-Hours Degradation

For services whose service tier permits it, escalation differs by time of day. State it as a table,
never as an unwritten norm:

| Service tier | Off-hours behaviour |
|--------------|--------------------|
| ST0 | Full chain, 24/7, no degradation |
| ST1 | Full chain 24/7, with Level 2 skipped where the rotation has no secondary; Level 5 (executive) business hours only, except a SEV1's leadership notice and any regulatory exposure, which go when they fall due — a statutory clock runs from discovery |
| ST2 | Page for SEV1 only; SEV2 becomes a business-hours ticket |
| ST3 | No off-hours paging; SEV2–4 queue to business hours. A genuine SEV1 still pages — and triggers a service-tier review, because an ST3 service should not be able to produce one |

Service tiers are defined by `operation-readiness`.

## Common Defects

- **Sequential-only escalation with long timeouts** — 15 minutes per level after Level 0 means
  30 minutes before a service owner is even paged; on a SEV1 the IC pool is paged on
  declaration (Level 4's trigger), so only the owner's wait is the defect here.
- **Escalation target is a rotation with the same people** — Level 2 pointing at a schedule
  where primary is also secondary.
- **Group inbox as an escalation target** — diffuse ownership means no acknowledgement.
- **No holiday-aware routing** — Level 3 is on annual leave and the chain silently terminates.
- **Untested chain** — run a deliberate no-acknowledge test quarterly. An escalation path
  that has never fired is a hypothesis.
