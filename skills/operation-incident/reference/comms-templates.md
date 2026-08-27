<!-- operation:deferred -->
# Incident Communication

Purpose: Internal cadence, customer notification thresholds, status page copy, all-clear.
Read when: internal cadence, customer notification thresholds, status page copy, all-clear
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## Principles

- **Communicate before you are asked.** The first stakeholder question is a communication failure.
- **Every update commits to the next update time.** No exceptions, including "no change".
- **Impact in user terms, never in system terms.** "Checkout is failing for EU customers", not
  "the payment service is returning 503s".
- **Never promise a resolution time** you cannot guarantee. Promise the next *update* time.
- **Mitigated ≠ resolved.** Say which. Telling customers "resolved" when the cause is still
  live is how a second outage becomes a credibility incident.
- **Own it.** Attributing to a third-party provider before it is proven — and often after —
  reads as deflection. The customer's relationship is with you.

## Audiences and Thresholds

| Audience | Notify when | Channel | Cadence |
|----------|-------------|---------|---------|
| Responders | Declaration | War room | Continuous |
| Engineering org | SEV1/SEV2 declaration | Team channel | On state change |
| Support team | Any customer-visible impact | Support channel, **before** the status page | 30 min at SEV1 |
| Leadership | SEV1, or SEV2 past 1h | Direct + channel | 30–60 min |
| Affected customers | Impact confirmed and reproducible | Status page, in-app, email | 30 min at SEV1 |
| All customers | Broad impact or trust-relevant | Status page + email | 30 min |
| Regulators | Statutory trigger met | Owned by legal/compliance — escalate, never send | Per statute |

**Support hears first.** They are already receiving the tickets; support learning about an
outage from the public status page is a process failure.

## Internal Update

```
INCIDENT <id> — SEV<n> — <status> — update <n>
IMPACT:    <who, what, since when — user terms>
CURRENT:   <what is being done right now>
NEXT:      <the next decision or action, and when>
ETA:       <mitigation ETA, or "no reliable ETA yet">
NEEDED:    <help required, or "none">
NEXT UPDATE: <HH:MM UTC (HH:MM local)>
```

## Customer — Initial

```
<Service> — <brief impact title>
Investigating — <HH:MM UTC>

We are aware of an issue affecting <what, in user terms> for <who>.
<Workaround, if any.>
We are investigating and will update by <HH:MM UTC>.
```

Do not include a cause. Early causal claims are wrong often enough that the correction costs
more trust than the silence would have.

## Customer — Update

```
<Service> — <brief impact title>
Identified | Monitoring — <HH:MM UTC>

<What is happening, in user terms.> <What we have done.>
<Current state: still affected / partially restored / restored and monitoring.>
Next update by <HH:MM UTC>.
```

## Customer — Resolution

```
<Service> — <brief impact title>
Resolved — <HH:MM UTC>

Between <start> and <end> UTC, <who> were unable to <what>.
The issue has been resolved and we have confirmed normal operation.
<If data was affected: precise scope and what customers should do.>
We are conducting a review and will <publish a postmortem / contact affected customers directly>.
```

If the fix is a mitigation rather than a cure, say `Monitoring`, not `Resolved`.

## Status Page Discipline

- Assign status-page updates to the **CL explicitly**. Unassigned, it is nobody's job, and a
  green status page during a SEV1 becomes its own incident.
- Post within 15 minutes of confirming customer-visible impact at SEV1.
- Component-level status must match reality — marking one component degraded while three are
  down understates and is noticed.
- Keep the incident open on the page through the monitoring period.
- Backfill the timeline on the page after resolution; customers use it to explain the outage
  to *their* customers.

## Executive Communication

Executives need decisions, not diagnostics:

```
<Service> SEV<n> — <elapsed>
Customer impact: <one line, quantified>
Revenue/regulatory exposure: <one line, or none identified>
Status: <mitigating | monitoring | resolved>
Decision needed from you: <specific ask, or none>
Next update: <HH:MM>
```

The CL owns this channel. Executives contacting the IC directly is a communication-structure
failure — redirect them to the CL rather than absorbing the interrupt.

## Regulatory Notification

**Never draft or send autonomously.** The role here is:

1. Identify that a trigger may have been met (`reference/impact-assessment.md`).
2. Record the **discovery timestamp** — statutory clocks usually run from discovery.
3. Escalate to legal/compliance immediately, with the impact statement and evidence.
4. Preserve evidence; log every access to affected data from that point on.

## Common Failures

- **Silence during long investigations.** Stakeholders assume abandonment and start their own
  parallel investigation, consuming the responders.
- **Committing to an ETA under pressure.** Missing it costs more than never giving one.
- **Technical language externally.** "Elevated 5xx" means nothing to a customer.
- **Declaring resolved during the monitoring period.** Recurrence after an all-clear is a far
  worse event than a longer incident.
- **The all-clear that never comes.** Incidents that fade out leave customers unsure, and
  support answering questions for weeks.
- **Different numbers to different audiences.** One impact statement, reused everywhere.
