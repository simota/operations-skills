<!-- operation:deferred -->
# Decommission

Purpose: Retiring a service, silent consumer discovery, unwind order, data retention.
Read when: retiring a service, silent consumer discovery, unwind order, data retention
Verified: 2026-08-21 — no automated check.

Retiring a service is a change with an unusually large blast radius and no rollback once data
is deleted. Treat every deletion step as `T4` (`_operation/SAFETY_TIERS.md`).

## Consumer Discovery

The step that determines whether decommissioning is safe. Request dashboards sampled over a
week will not find everything.

| Consumer type | How to find it |
|---------------|----------------|
| Synchronous API callers | Access logs over ≥1 full business cycle |
| Batch jobs | Scheduler inventory; monthly and quarterly jobs will not appear in a week |
| Partner and third-party integrations | Contracts, API keys issued, egress logs |
| Internal tools and scripts | Code search across all repos, including personal and ops repos |
| Scheduled reports | Reporting tool inventory |
| Webhooks and callbacks | Outbound configuration in the service itself |
| Data consumers | Pipelines reading its database or object storage directly |
| Humans | Ask; some consumers are a person with a bookmark |

**Watch for a full business cycle** — at minimum one month, and one quarter for anything with
quarterly reporting. The consumer nobody knew about is almost always a monthly job.

## Unwind Order

1. **Announce** — with a date, to every discovered consumer, with a migration path.
2. **Stop new consumers** — remove from catalogs, revoke new key issuance, mark deprecated.
3. **Migrate known consumers** — track each to completion individually.
4. **Darkening test** — refuse traffic for a controlled window and see who surfaces. Design
   it as a staged, observed test, not as an outage (see below).
5. **Stop serving** — keep the service deployed but idle. Reversible.
6. **Stop running** — undeploy. Keep the artifact and configuration.
7. **Hold the verification window** — one full business cycle with **alerting, dashboards, and
   the on-call rotation still in place**, so that a missed consumer surfacing in a monthly job
   is detected and someone is paged for it.
8. **Retire operational surface** — alerts, runbooks, dashboards, and the rotation entry, only
   after the verification window closes clean.
9. **Retain data** for the required period, offline, with a documented restore path.
10. **Delete data** — `T4`, after the retention period, with explicit approval.

**Observability is retired last, not first.** Steps 1–8 are reversible, and a reversal is only
safe if the service comes back with its detection intact — retiring alerts while the service
can still be turned back on produces a running service nobody is watching.

Step 10 is irreversible. The gap between step 8 and step 10 is the safety margin, and it
should be measured in months for anything above T3.

### Darkening Test Design

Deliberately failing production traffic is a `T3` action and is designed as an experiment, not
as a 24-hour outage:

- **Stage the windows**: 5 minutes → 1 hour → 1 business day, with a clean result required
  before each escalation.
- **Business hours only**, with a re-enable path exercised beforehand and a named watcher.
- **Instrument it** — the detection signal is the request log, error rate, and downstream
  error rate, *not* "who complains". Complaints are the slowest and least complete signal, and
  relying on them alone means silent consumers stay silent and break later.
- **Return an explicit, identifiable error** (a distinct status and message naming the
  decommission), so a caller's logs point at the cause instead of a generic failure.
- **Abort immediately** on any impact outside the expected consumer set.
- **Never darken a T0 or T1 service without an incident-grade plan** — at those tiers, run the
  test in a mirrored or single-region scope first.

## Data Retention

- Determine the requirement **before** starting: regulatory, contractual, and internal.
- Retain offline in a form that can actually be read later — a database dump requiring a version
  of the software nobody runs any more is not retention.
- Document the restore path and test it once.
- Record the deletion date and who approves it.
- Verify no other system holds a foreign key or reference into the retained data.

## Operational Surface Retirement

Frequently forgotten, and it leaves debris that confuses responders for years:

- [ ] Alerts deleted, not merely silenced — a silence expires and pages someone about a service
      that no longer exists
- [ ] Runbooks retired, with inbound links checked and updated
- [ ] Dashboards removed or archived
- [ ] Rotation entry removed; recompute the remaining pool size
- [ ] Escalation policies updated — check whether anyone was a fallback only for this service
- [ ] Status page component removed
- [ ] On-call documentation and onboarding material updated
- [ ] Monitoring and log ingestion stopped (this is often a meaningful cost line)
- [ ] Credentials, service accounts, and API keys revoked
- [ ] DNS entries removed, after confirming nothing resolves them
- [ ] CI/CD pipelines removed
- [ ] Dependency graphs updated in every service that listed it

## Post-Decommission Verification

After each irreversible step, verify:

- No error rate increase in any downstream or adjacent service
- No new support tickets referencing the capability
- No failed scheduled jobs
- Cost reduction actually materialised — if not, something is still running

This is step 7 — hold it for at least one full business cycle after undeploying, with alerting
still active, before retiring the operational surface (step 8) or deleting data (step 10).
