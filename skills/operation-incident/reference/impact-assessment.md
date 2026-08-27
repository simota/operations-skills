<!-- operation:deferred -->
# Impact Assessment

Purpose: Scoping user/feature/data/financial/regulatory impact, capturing volatile evidence.
Read when: scoping user/feature/data/financial/regulatory impact, capturing volatile evidence
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

Two jobs, in this order: **capture what is about to disappear**, then **scope what is broken**.

## 1. Volatile Evidence Capture

Do this before any restart, redeploy, scale, or failover. Budget 60 seconds; it is cheaper
than an unexplainable postmortem.

**The exception, and it is a real one:** when impact is actively compounding — data being
written incorrectly, a leak spreading, an attacker active, a queue irrecoverably filling —
stop the bleeding first and capture what survives afterwards. Evidence is worth 60 seconds of
a steady-state outage; it is not worth 60 more seconds of corruption. The IC makes this call
explicitly and the Scribe records that capture was skipped and why.

| Evidence | Lifetime | Capture |
|----------|----------|---------|
| Process state, thread/goroutine dumps, heap | Until restart | Dump to durable storage |
| In-flight request state | Seconds | Sample logs of active requests |
| Container/pod state and events | Until reschedule | Describe/inspect output |
| Debug-level logs | Hours to days | Export the incident window **now** |
| Dashboard panels | Relative ranges shift | Screenshot + absolute-time permalink |
| Queue depth and consumer positions | Continuously changing | Snapshot offsets |
| Connection pool / thread pool state | Until restart | Metrics snapshot |
| DNS, routing, certificate state | Until propagation | Query and record output |
| Feature flag values | Until next change | Export the current evaluation |
| Recent change log | Days | List deploys/config changes in the window |

**Log retention is shorter than postmortem lead time.** Export at `ASSESS`, not at write-up.

## 2. Impact Dimensions

| Dimension | Questions | Evidence source |
|-----------|-----------|-----------------|
| **Users** | How many? Which segments, regions, tiers? Are enterprise/paying users over-represented? | SLI by segment, request logs |
| **Functionality** | Which workflows fail entirely vs degrade? Is there a workaround, and do users know it? | Endpoint-level error rates |
| **Data** | Loss? Corruption? Staleness? Unauthorised exposure? Is the affected window bounded? | Integrity checks, audit logs |
| **Financial** | Failed transactions, value at risk, SLA credits, ongoing burn rate per hour | Payment/order metrics |
| **Regulatory** | Personal data exposed? Notification clock started? Which jurisdictions? | Data classification, access logs |
| **Trust** | Public visibility, customer escalations, press or social attention | Support queue, social monitoring |
| **Internal** | Blocked teams, blocked deploys, consumed responder capacity | Deploy queue, on-call load |

## Scoping Discipline

- **Unknown scope defaults to the worst plausible case** until bounded. "We don't know how many
  users" is treated as "all users" for severity purposes and corrected as evidence arrives.
- **Bound the time window explicitly.** "Started at 13:42Z" — is the start the first error, the
  deploy, or the config change? State which, and how it was determined.
- **Look for silent impact.** Requests failing loudly are visible; the dangerous cases are the
  silent ones — writes accepted and discarded, jobs skipped, events dropped, stale cache served
  as fresh. Explicitly ask: what could be failing without producing an error?
- **Check the blast radius beyond the obvious.** Downstream consumers, batch jobs due during the
  window, webhooks and callbacks, scheduled reports, partner integrations, and anything that
  retries into the failure.

## Data Impact Triage

The dimension most often assessed too late.

1. **Is data being written incorrectly right now?** If yes, stopping the writes takes priority
   over restoring availability — availability is recoverable, corrupted data may not be.
2. **Is the affected window bounded?** Identify the first and last affected record.
3. **Is it detectable after the fact?** If corrupted records are indistinguishable from good
   ones, say so immediately — this changes the entire response.
4. **Is it recoverable?** From backup, from replay, from an upstream source, or not at all.
5. **Has it propagated?** Caches, replicas, downstream systems, exports, third parties.

Data impact is a `T4` domain (`_operation/SAFETY_TIERS.md`) — repair actions are proposed, never
executed autonomously.

## Regulatory Trigger Check

Run this check on every incident touching personal data, payment data, or availability
commitments. Do not attempt to interpret the obligation — identify the trigger and escalate
to whoever owns it.

- [ ] Was personal data exposed to an unauthorised party, or possibly exposed?
- [ ] Was the exposure to an internal party without a legitimate need?
- [ ] Is there a contractual notification commitment to any customer?
- [ ] Does an SLA credit clause trigger?
- [ ] Is a sector-specific regulator involved (financial, health, telecom)?

Any checked box: escalate immediately with the timestamp of discovery. Statutory clocks
typically run from **discovery**, not from confirmation — delay in escalating is itself a
compliance risk.

## Impact Statement Format

Used in every communication and in the postmortem. Reusable, precise, no hedging:

```
Between <start UTC> and <end UTC | ongoing>, <who — segment and approximate count>
experienced <what, in user terms>.
Workaround: <what users can do | none>.
Data: <no data affected | scope of data impact, bounded>.
Detection: <how it was found, at what time>.
```

"Users in the EU region were unable to complete checkout" — not "the payment service
experienced elevated error rates". Users do not have error rates.
