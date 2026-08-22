<!-- operation:guidance -->
# Readiness Verdict, Tier Requirements

## Readiness Verdict

```yaml
service: "<name>"
tier: T0 | T1 | T2 | T3
reviewed: <YYYY-MM-DD>
reviewer: "<named individual>"
verdict: GO | GO WITH CONDITIONS | NO-GO
blocking_findings:
  - finding: "<what is missing or wrong>"
    evidence: "<rung and source>"
    owner: "<named individual>"
    due: <YYYY-MM-DD>
non_blocking_findings:
  - finding: "<...>"
    owner: "<...>"
    due: <YYYY-MM-DD>
accepted_risks:
  - risk: "<blocking finding being launched with>"
    accepted_by: "<named individual, not a team>"
    review_by: <YYYY-MM-DD>
capacity:
  current_peak: "<value>"
  headroom: "<multiple of current peak, verified how>"
  next_ceiling: "<what saturates first, at what value>"
not_covered:
  - "<what this review did not examine>"
```

`not_covered` is mandatory. A review that implies full coverage it did not perform is worse
than a narrow one that says so.

## Tier Requirements

| Requirement | T0 (critical) | T1 (important) | T2 (standard) | T3 (best effort) |
|-------------|---------------|----------------|---------------|------------------|
| Availability target | Defined SLO, error budget policy | Defined SLO | Target, no budget policy | None |
| On-call | 24/7 primary + secondary | 24/7 primary | SEV1 only off-hours | Business hours |
| Runbook coverage | All paging alerts, all `CURRENT` | All paging alerts | Top failure modes | Best effort |
| Rollback | Verified, exercised ≤90 days | Verified, exercised ≤180 days | Documented | Documented |
| Capacity headroom | ≥3× current peak, load tested | ≥2× current peak | ≥1.5× | None |
| DR / failover | Tested ≤6 months | Tested ≤12 months | Documented | None |
| Postmortem | All SEV1/SEV2 | All SEV1/SEV2 | SEV1 | On repeat |
| Escalation depth | Full chain | Full chain, exec tier business hours | Two tiers | One tier |
| Change approval | Two reviewers above risk 15 | Service owner | Service owner | None |
| Dependency tier floor | All deps ≥ T0 | All deps ≥ T1 | All deps ≥ T2 | None |

This table is canonical; `reference/service-tiering.md` covers how the tier is derived, not
what it requires.

**A service cannot be more available than its least available dependency.** A dependency
tiered below the service is a **blocking** finding at T0, T1, and T2 — not only at T0. The
exceptions are narrow and must be demonstrated, not asserted: the dependency is genuinely
optional (the service degrades gracefully and that path is tested), or it is redundant across
independent providers. "We cache it" is an exception only if the service is verified to run
for the full outage budget on cache alone.
