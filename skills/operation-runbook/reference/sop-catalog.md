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
- Start with the **verb** — responders search by what they need to do.
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
| Review cadence | By tier: T4 quarterly, T3 semi-annually, T1–T2 annually |
| Last executed | Date, updated on every real execution |

An owner who has left is the most common catalog defect. Check ownership validity during audits
before checking content.

## Freshness

**Freshness is measured by last execution, never by last edit.** A document edited yesterday
but not run in a year is more dangerous than an honest old one — the edit signals currency that
the content does not have.

| Age since last execution | Status | Action |
|--------------------------|--------|--------|
| < review cadence | `CURRENT` | None |
| 1–2× cadence | `STALE` | Schedule a game-day execution |
| > 2× cadence | `UNVERIFIED` | Mark it in the header; responders must know before relying on it |
| Never executed | `UNVERIFIED` | Must be tested before an alert may link to it |

Runbooks for rare events (disaster recovery, region failover) will never accumulate real
executions — they require **scheduled** rehearsals, and their status is driven by rehearsal
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
| Linked runbooks with status `CURRENT` | ≥80% |
| Linked runbooks never executed | 0 |

Gaps route to `operation-oncall` as `KEEP (conditional)` alerts — page-worthy but undocumented.

## Audit Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| `CURRENT` | Executed within cadence, owner valid, content matches reality | None |
| `STALE` | Content plausible, not executed recently | Schedule a rehearsal |
| `DRIFTED` | Content contradicts the current system (commands, paths, flags changed) | Fix now; a drifted runbook is worse than none |
| `UNVERIFIED` | Never executed end to end | Test before any alert links to it |
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
