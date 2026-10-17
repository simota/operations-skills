<!-- operation:deferred -->
# SOP Catalog Governance

Purpose: Naming, versioning, ownership, discoverability, freshness decay, alert-to-runbook coverage.
Read when: naming, versioning, ownership, discoverability, freshness decay, alert-to-runbook coverage
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## Naming

`<service>/<verb>-<object>[-<qualifier>]`

```
payments-api/rollback-deploy
payments-api/rotate-db-credentials
kafka/rebalance-partitions
platform/restore-postgres-from-backup
```

Rules:
- After the service prefix, start with the **verb** — responders search by what they need to do.
- One procedure, one file. A file covering "database operations" is an index, not a runbook.
- No dates, ticket numbers, or author names in the filename.
- No `-v2`, `-new`, `-final`. Version in git, not in the name.

## Ownership

Every runbook names a **single individual**, not a team. Team ownership means nobody notices
when it rots.

| Field | Requirement |
|-------|-------------|
| Owner | Named individual, currently employed, verified quarterly |
| Backup owner | A second individual, for the case where the owner is the incident |
| Expiry interval | By safety tier, shorter where the system changes faster: T4 quarterly, T3 semi-annually, T1–T2 annually — and never longer than the service tier's cadence for the same path (`operation-readiness`'s tier requirements: rollback ≤90 days at ST0, ≤180 at ST1) |
| Voiding surface | The named surface whose change expires the proof at once (`_operation/EXPIRY.md`) |
| Last executed | Date, by whom, and where — updated only by a real execution |

An owner who has left is the most common catalog defect. Check ownership validity during audits
before checking content.

## Freshness

**Freshness is measured by last execution, never by last edit.** A document edited yesterday
but not run in a year is more dangerous than an honest old one — the edit signals currency that
the content does not have.

| Condition | State | Action |
|-----------|-------|--------|
| Executed in production within its expiry, voiding surface unchanged | `proved` | None |
| Executed only in a lower environment, or the destructive step stubbed | `simulated` | Rely on it only with the gap stated; schedule a real execution |
| Expiry interval passed, or the voiding surface changed | `stale` | `UNVERIFIED` — no plan may depend on it; mark the header and re-run; an alert that otherwise pages stays `KEEP (conditional)` |
| Never executed | `untested` | `UNVERIFIED` — an alert may link to it only with the `untested` state visible at the link, and an alert that otherwise pages stays `KEEP (conditional)` until it is executed |
| Cannot be exercised without unacceptable cost or risk | `unprovable` | Name the compensating control and its owner |

Runbooks for rare events (disaster recovery, region failover) will never accumulate real
executions — they require **scheduled** rehearsals, and their state is driven by rehearsal
dates, not incidents.

## Discoverability

The catalog fails if a responder cannot find the right runbook in under 60 seconds at 3 a.m.

- **Alert → runbook link is the primary path.** Every paging alert links directly to the
  specific procedure, not to a wiki index.
- **Symptom index**, organised by what the responder observes, not by system internals: "checkout
  returns 500" finds the runbook; "payment gateway circuit breaker" does not, because the
  responder does not know that yet.
- **Search that covers content**, including command strings — responders search for the error
  message they are looking at.
- **Co-located with code** where practical. Runbooks in the service repo drift less, because
  they are visible in the diff that breaks them.
- **Offline-reachable.** A runbook for "the wiki is down" that lives on the wiki is not a runbook.
  `T4` and disaster-recovery procedures need an out-of-band copy.

## Alert-to-Runbook Coverage

The single most valuable catalog metric.

| Metric | Target |
|--------|--------|
| Paging alerts with a runbook link | 100% |
| Links resolving to a specific procedure (not an index) | 100% |
| Linked runbooks `proved`, or `unprovable` with a compensating control | 100% — each `stale` one is an `UNVERIFIED` residual, named |
| Linked runbooks never executed | 0 — each one is an `UNVERIFIED` residual, its alert `KEEP (conditional)` |

Gaps route to `operation-oncall` as `KEEP (conditional)` alerts — page-worthy but undocumented,
or documented by a runbook that is `UNVERIFIED`: never executed, its proof expired, or its gap or
control unstated (`_operation/EXPIRY.md`).

## Audit Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| `proved` | Executed within its expiry, owner valid, content matches reality | None |
| `stale` | Content plausible, expiry passed or voiding surface changed | Schedule a rehearsal |
| `DRIFTED` | Content contradicts the current system (commands, paths, flags changed) | Fix now; a drifted runbook is worse than none |
| `simulated` | Executed only in a lower environment, or with the destructive step stubbed | Rely on it only with the gap stated; schedule a production rehearsal |
| `untested` | Never executed end to end | Have a person execute it; until then any alert linking to it shows `untested`, and one that otherwise pages stays `KEEP (conditional)` |
| `unprovable` | Cannot be exercised without unacceptable cost or risk | Confirm the compensating control and its owner; prove the smallest part that can be |
| `ORPHANED` | Owner has left, or no owner | Reassign or retire |
| `RETIRE` | The procedure or the system it targets no longer exists | Delete, and check nothing links to it |

`DRIFTED` is the most dangerous state: it carries the authority of a document while giving
instructions that fail. Prioritise `DRIFTED` above every gap.

## Retirement

- Check for inbound links (alerts, other runbooks, onboarding docs) before deleting.
- Record why it was retired, in the commit message.
- If the system still exists but the procedure is superseded, link forward from the old file
  rather than deleting it — responders have the old link bookmarked.
- Never leave a retired runbook in place "just in case". A superseded procedure that still
  looks live will be followed.
