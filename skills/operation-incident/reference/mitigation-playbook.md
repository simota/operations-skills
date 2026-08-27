<!-- operation:deferred -->
# Mitigation Playbook

Purpose: Choosing rollback vs fix-forward vs degrade vs failover, time-boxing, verification.
Read when: choosing rollback vs fix-forward vs degrade vs failover, time-boxing, verification
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## The Options

Always enumerate all five, including "do nothing". Each carries a `SAFETY_TIER`.

| Option | Time to effect | Use when | Risk |
|--------|---------------|----------|------|
| **Roll back** | Minutes | Impact correlates with a recent change and the change is reversible | Migrations may make it irreversible |
| **Fix forward** | Tens of minutes to hours | Rollback is impossible, or cause is known and the fix is trivial | Untested code under pressure |
| **Degrade** | Minutes | Partial service beats none — disable the failing feature, serve stale, shed load | Silent partial failure if not communicated |
| **Fail over** | Minutes | Failure is localised to a zone, region, provider, or replica | Untested failover creates a second incident; unmeasured replication lag loses writes |
| **Do nothing, observe** | — | Impact is transient, self-healing is underway, or action risks making it worse | Elapsed time is a real cost |

"Do nothing" being an explicit option matters: incident pressure biases toward action, and
some actions extend outages.

## Decision Framework

Choose by **shortest verified path to impact ending**, not by elegance.

1. Is impact correlated with a change in the last 24h? → Rollback is the first hypothesis.
2. Is rollback genuinely reversible? Check migrations, schema versions, data formats,
   feature-flag dependencies, and cache/message formats. If a migration ran, rollback may be
   `T4`, not `T2`.
3. Is there a runbook for this failure mode? → Execute it. This is what
   `operation-runbook` exists for.
4. Is the cause known with `O2` evidence? → Fix forward is viable.
5. Cause unknown and impact severe? → Degrade or fail over. Restore service, then diagnose.
6. None available? → Escalate for more expertise; state explicitly that no mitigation is
   currently identified. This is a valid, communicable state.

## Rollback Reversibility Check

Before treating rollback as safe, confirm:

- [ ] Did a schema migration run? Is it backwards-compatible with the previous version?
- [ ] Did the new version write data in a format the old version cannot read?
- [ ] Did message/event formats change for in-flight or queued messages?
- [ ] Did cache key formats or serialisation change?
- [ ] Are there dependent services already upgraded to expect the new behaviour?
- [ ] Do feature flags need reverting alongside the code?

Any "yes" without a compatible path makes rollback `T3`/`T4` and it needs the same scrutiny as
a fix forward. **Rolling an application back into an incompatible schema converts an outage
into data loss** — this is one of the most common ways an incident gets worse.

## Time-Boxing

Every diagnostic line of enquiry gets an explicit budget, announced by the IC:

| Severity | Default hypothesis budget | On expiry |
|----------|--------------------------|-----------|
| SEV1 | 15 min | Switch to blunt mitigation (rollback, restart, failover, shed) |
| SEV2 | 30 min | Reassess options; consider degrade |
| SEV3 | 2h | Convert to a ticket if impact is stable |

At expiry the IC makes a deliberate call: extend with a stated reason, or switch. Silent
overrun is the mechanism by which a 20-minute outage becomes a three-hour one.

## Blunt Mitigations

Crude, fast, and frequently correct when the cause is unknown:

| Action | Effect | Tier | Caution |
|--------|--------|------|---------|
| Restart the affected instances | Clears corrupt in-memory state | T2 | Destroys evidence — capture first |
| Roll back the last change | Removes the likely trigger | T2–T4 | Check migration reversibility |
| Scale out | Absorbs load-driven failure | T2 | Amplifies a downstream bottleneck |
| Shed load / rate limit | Protects the core for most users | T3 | Choose *whose* traffic is dropped deliberately |
| Disable the feature flag | Removes the failing path | T2 | Verify the flag actually gates the code path |
| Fail over | Escapes localised failure | T3 if failback exercised, else **T4** | See Failover Safety below — fence before promote |
| Serve stale / cached | Preserves reads during a write failure | T3 | Communicate staleness to users |
| Drain and isolate a bad node | Removes a single bad actor | T2 | Confirm it is actually the outlier |

## Failover Safety

Failover is the mitigation most likely to convert an outage into permanent data loss, and the
tier depends entirely on whether failback and write-topology are understood
(`_operation/SAFETY_TIERS.md`).

Before failing over, answer all four:

| Question | If the answer is bad |
|----------|---------------------|
| **What is the replication lag right now?** | Failing over with N seconds of lag discards N seconds of accepted writes. Quantify it; do not assume "async, probably fine" |
| **Can both sides accept writes after the cut?** | If yes, you have split-brain. Fence the old primary *before* promoting the new one, not after |
| **Is the old primary actually dead, or just unreachable?** | An unreachable-but-alive primary still serving writes is the classic split-brain trigger. Network partition ≠ node failure |
| **What reconciles divergence afterwards?** | If nothing does, divergence is silent data corruption discovered weeks later |

Rules:
- **Fence before promote.** Isolate the old primary (STONITH, revoke its credentials, drop its
  routes) and confirm the isolation, then promote. Promoting first is how both sides end up live.
- **Record the failover timestamp and the lag at that moment.** It bounds the window of
  potentially lost writes, and the postmortem and any customer notification both need it.
- **A failover with unexercised failback is `T4`**, not `T3` — you are committing to the new
  region with no verified way back.
- **Quorum systems**: confirm the surviving side actually has quorum. Promoting a minority
  partition produces a cluster that accepts writes and later discards them.
- If replication lag cannot be measured, treat the failover as lossy and communicate it as such.

## Emergency Credential Containment

Distinct from planned rotation. When a credential is believed compromised, the operational
problem is that revoking it breaks every legitimate user of it simultaneously.

Order matters:

1. **Scope it** — what does the credential grant, and which services present it? Enumerate
   before acting; a revocation of unknown scope is an unbounded outage.
2. **Issue the replacement first.** Never revoke before the new credential is deployed and
   verified in use — that is a self-inflicted outage on top of the compromise.
3. **Contain without revoking**, where the platform allows it: IP-allowlist the credential,
   rate-limit it, or scope it down. This buys the time to do step 2 safely.
4. **Cut the sessions, not just the credential.** Revoking an API key does not end sessions
   already issued from it. Invalidate derived tokens and sessions explicitly, or the attacker
   keeps access after the key is dead.
5. **Then revoke**, and confirm the old credential now fails.
6. **Preserve the audit trail** — every use of the credential in the exposure window is
   evidence, and log retention is usually shorter than the investigation.

Steps 1–4 are `T3`. Step 5 is `T4` (it is the irreversible one). If the compromise is active
and being exploited, the tier order inverts — revoke first and accept the outage — but that is
an Incident Commander decision, stated explicitly, not a default.

Deep security analysis of the compromise itself is out of scope (`_operation/ROUTING.md`); this
covers only keeping the service running while the credential is replaced.

## Verification Before All-Clear

The alert going quiet is not recovery. Verify in this order:

1. **User-path probe** — a synthetic transaction or manual request through the real user path,
   end to end. Metrics, logs, and traces are also `O1` (`_operation/CONTRACT.md`), but they are
   `O1` about *the system*; only the probe is `O1` about **the user's experience**, which is
   what recovery means. Do not substitute a green dashboard for it.
2. **SLI recovery** — the user-facing *instantaneous* indicator back at baseline, not merely
   improving. Do **not** gate the all-clear on a long-window SLO returning inside target: a
   30-day rolling SLO stays violated for weeks after a real recovery, and waiting on it holds
   the incident open long after users are whole. Track the burn *rate* returning to normal;
   the budget consumed is a postmortem input, not an all-clear gate.
3. **Error budget** — confirm burn has stopped, not just slowed.
4. **Backlog drained** — queues, retries, and dead-letter queues processed. Recovery with a
   million queued retries is a pending second incident.
5. **Downstream confirmation** — dependent systems and partners recovered.
6. **Data reconciliation** — anything written during the window is verified or quarantined.
7. **Monitoring period** — hold before all-clear: SEV1 30 min, SEV2 15 min. Premature
   all-clears cost more credibility than a slow one.

Explicitly verify the monitoring itself recovered — if the exporter died, the graphs look
perfect for exactly the wrong reason.

## Mitigation Failure

When a mitigation does not work:

- Say so immediately in the war room and in the next comms update. A failed mitigation quietly
  absorbed leaves stakeholders believing recovery is imminent.
- **Revert the failed mitigation before trying the next one**, unless it is provably harmless.
  Stacked partial mitigations produce a system state nobody can reason about, and a postmortem
  nobody can reconstruct.
- Upgrade severity if the failure means impact will continue materially longer.
- Record the attempt, its rationale, and its outcome — failed mitigations are among the most
  valuable postmortem content, and the most commonly omitted.
