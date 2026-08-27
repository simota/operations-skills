<!-- operation:deferred -->
# Alert Hygiene

Purpose: Auditing an alert corpus, applying the four paging criteria, grouping/suppression design, noise-source attribution.
Read when: auditing an alert corpus, applying the four paging criteria, grouping/suppression design, noise-source attribution
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## The Four Paging Criteria

An alert may page a human only if **all four** hold:

1. **Impact** — it indicates user-visible impact, or impact that will occur without action.
2. **Agency** — a human action can change the outcome.
3. **Non-automatable** — that action cannot be reliably automated today.
4. **Documented** — the action is written down and reachable from the alert.

Which criterion fails decides the verdict — they are not interchangeable:

| Failing | Verdict | Because |
|---------|---------|---------|
| (2) agency | `DELETE` | No human action can ever change the outcome |
| (1) impact, but (2) holds | `DEMOTE` to ticket | Real and actionable, but no user consequence |
| (3) non-automatable | `DEMOTE` + automate | A human is doing a machine's job |
| (4) documented | `KEEP (conditional)` | Still pages; the missing runbook is a blocking gap |

Failing both (1) and (2) is `DELETE`. Note that a `KEEP (conditional)` alert **keeps paging** —
the "conditional" marks the runbook debt, it does not suspend the page. Silencing a real
user-impact alert because its runbook is unwritten trades a documentation gap for an outage.

## Audit Procedure

For each alert, collect over a 30–90 day window:

| Field | Source | Used for |
|-------|--------|----------|
| Fire count | Alerting tool history | Volume ranking |
| Distinct-incident count | Correlate fires to incidents | Flap detection |
| Self-resolve count | Fires closed without human action | Agency test |
| Median time-to-ack | Paging tool | Perceived importance |
| Action taken (free text) | Incident/ticket notes | Automatability test |
| Co-fire partners | Timestamp correlation | `MERGE` candidates |
| Runbook link present | Alert definition | Documentation test |

An alert with no fires in 90 days is not automatically healthy — check whether the condition
is even reachable. Untested alerts fail silently when they are finally needed.

## Verdicts

| Verdict | Meaning | Required output |
|---------|---------|-----------------|
| `KEEP` | Passes all four criteria | Reason + runbook link |
| `KEEP (conditional)` | Passes 1–3, missing runbook | Blocking gap handed to `operation-runbook` |
| `DEMOTE` | Real but not page-worthy | Target channel + response SLA |
| `MERGE` | Redundant with a parent symptom alert | Parent alert name |
| `DELETE` | No impact or no agency | What would be lost, and what still covers it |

Every `DELETE` states its coverage successor or explicitly states there is none. Deleting
the only signal for a failure mode is a decision, not housekeeping.

## Noise Source Attribution

Most noise concentrates. Rank sources before fixing individual alerts:

| Source | Signature | Fix |
|--------|-----------|-----|
| Flapping | Same alert, many fires, short duration | `for:` duration / hysteresis, not threshold change |
| Cause-based alerting | Alerts on CPU/memory/disk with no user impact | Replace with symptom alerts on the user-facing SLI |
| Missing grouping | N replicas → N identical pages | Group by service, not instance |
| Static thresholds on seasonal traffic | Fires every peak | Rate-of-change or burn-rate alerting |
| Dependency cascade | One root failure pages six teams | Alert on the dependency, inhibit downstream |
| Test/staging leakage | Non-prod firing into prod channel | Route by environment label |
| Deploy-correlated | Fires within minutes of every release | Deploy-aware suppression window with hard expiry |

## Grouping and Suppression

**Group by** the smallest unit a human would act on — usually `service` + `alertname` +
`environment`. Grouping by `instance` defeats the purpose; grouping by `team` merges unrelated
failures.

**Inhibition rules** — a higher-level symptom suppresses its known downstream noise:

```
inhibit: ServiceDown  suppresses  HighLatency, ErrorRateHigh   (same service)
inhibit: RegionUnreachable  suppresses  ServiceDown            (same region)
```

Inhibition without a corresponding "root alert exists" check is dangerous: if the root alert
is itself broken, everything downstream is silenced too. Test inhibition chains by disabling
the root and confirming downstream still fires.

**Suppression/silence rules:**

- Every silence carries an expiry. Maximum default: 24h.
- Silences longer than 24h require a named owner and a linked ticket.
- A silence renewed three times is a `DELETE`/`DEMOTE` candidate — the team has already
  decided this alert is not page-worthy.
- Never silence by wildcard across a whole service during an incident; silence the specific
  known-noisy alert.

## Symptom vs Cause

Page on symptoms. Cause-based alerts fire on conditions that *usually* precede impact and are
the dominant source of unactionable pages.

| Cause alert (demote) | Symptom alert (keep) |
|----------------------|----------------------|
| CPU > 90% | Request latency p99 > SLO |
| Disk 85% full | Write failures / 5xx |
| Pod restarted | Availability SLI burn rate |
| Queue depth > 10k | Consumer lag past the freshness SLO |
| Certificate expires in 7 days | *(exception — keep as ticket, not page)* |

**Exception: predictable, dated, irreversible failures** (certificate expiry, licence expiry,
quota exhaustion with a known date) are legitimately cause-based. They become tickets with a
lead time, and only page once inside the last-resort window.

## Alert Definition Checklist

Every `KEEP` alert must carry:

- [ ] Name describing the *user-visible symptom*, not the internal metric
- [ ] Severity mapped to a paging channel
- [ ] Owning team, resolvable to humans today
- [ ] Runbook URL that opens to the *specific* procedure, not a wiki index
- [ ] A one-line statement of what the user is experiencing right now
- [ ] Dashboard/query link for immediate context
- [ ] `for:` duration appropriate to the signal's noise floor
- [ ] Environment label
