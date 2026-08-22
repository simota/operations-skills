<!-- operation:guidance -->
# Paging Decision Table, Rotation Health Thresholds

## Paging Decision Table

Apply to every alert. The first row that matches decides.

| Condition | Verdict | Channel |
|-----------|---------|---------|
| No human action can change the outcome | `DELETE` | — |
| Action exists and is fully automatable today | `DEMOTE` | Auto-remediation + ticket on failure |
| Fires with another alert >80% of the time | `MERGE` | Into the parent symptom alert |
| No user impact, no imminent impact | `DEMOTE` | Ticket, business hours |
| User impact, action documented, not automatable | `KEEP` | Page primary |
| User impact, action NOT documented | `KEEP` (conditional) | Page primary — and the missing runbook is a blocking gap |
| Impact spans multiple services or is customer-announced | `KEEP` | Page primary + declare incident |

`KEEP (conditional)` is a debt marker: the alert pages today but is listed as a blocking
gap in the output, handed to `operation-runbook`.

## Rotation Health Thresholds

| Metric | Healthy | Warning | Defect |
|--------|---------|---------|--------|
| Pages per 24h shift | ≤2 | 3–5 | >5 |
| Off-hours pages (22:00–08:00) per shift | ≤1 | 2 | >2 |
| Actionability ratio (pages requiring human action) | ≥80% | 50–79% | <50% |
| Self-resolve rate | <10% | 10–25% | >25% |
| MTTA (page → acknowledged) | <5 min | 5–15 min | >15 min |
| Night-shift burden per responder | ≤1 week in 6 | 1 in 4–5 | more than 1 in 4 |
| Consecutive on-call weeks | 1 | 2 | ≥3 |

A `Defect` reading is reported as a defect in the system, with the remediation owner named.
Two or more `Defect` readings simultaneously → recommend pausing non-critical alert
additions until the corpus is triaged.
