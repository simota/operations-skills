<!-- operation:guidance -->
# Paging Decision Table, Rotation Health Thresholds

## Paging Decision Table

Apply to every alert. The first row that matches decides.

| Condition | Verdict | Channel |
|-----------|---------|---------|
| No human action (fix, comms, escalation) can change the outcome | `DELETE` the page; keep the signal if forensics reads it | — |
| Action exists and working automation already performs it | `DEMOTE` | Auto-remediation; a failed run is judged by the rows below, and pages only if one of them pages |
| Fires with another alert >80% of the time | `MERGE` | Into the parent symptom alert |
| No user impact, no imminent impact | `DEMOTE` | Ticket, business hours |
| Impact spans multiple services or is customer-announced | `KEEP` | Page primary + declare incident; an undocumented action is still a blocking gap |
| User impact, runbook written and neither `untested` nor `stale`, no working automation | `KEEP` | Page primary |
| User impact, action NOT documented, or its runbook `untested` or `stale` | `KEEP` (conditional) | Page primary — and the missing or unproven runbook is a blocking gap |

`KEEP (conditional)` is a debt marker: the alert pages today but is listed as a blocking
gap in the output, handed to `operation-runbook`.

`DELETE` removes the page, not the signal: telemetry a postmortem or forensics would read is kept
as a non-paging recording, and the verdict says so. Automation that exists but does not work is
not a reason to demote — the remaining rows decide, as if no automation existed.

## Rotation Health Thresholds

| Metric | Healthy | Warning | Defect |
|--------|---------|---------|--------|
| Pages per 24h shift | ≤2 | 3–5 | >5 |
| Off-hours pages (22:00–08:00, responder's local time) per week on call | ≤1 | 2 | >2 |
| Actionability ratio (pages requiring human action) | ≥80% | 50–79% | <50% |
| Self-resolve rate | <10% | 10–25% | >25% |
| MTTA (page → acknowledged) | <5 min | 5–15 min | >15 min |
| Night-shift burden per responder | ≤1 week in 6 | 1 in 4–5 | more than 1 in 4 |
| Consecutive on-call weeks | 1 | 2 | ≥3 |

The **page budget** is the `Healthy` ceiling of the first two rows: ≤2 pages per 24h shift and
≤1 off-hours page per week on call. A `Defect` reading is reported as a defect in the system, with the remediation owner named.
Two or more `Defect` readings simultaneously → recommend pausing non-critical alert
additions until the corpus is triaged.
