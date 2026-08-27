<!-- operation:deferred -->
# On-call Health

Purpose: Diagnosing rotation health, burnout leading indicators, metric definitions and collection.
Read when: diagnosing rotation health, burnout leading indicators, metric definitions and collection
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## Metric Definitions

Precise definitions matter — most disputes about on-call load are definitional.

| Metric | Definition | Collection |
|--------|------------|------------|
| Pages per shift | Notifications that reached a human, deduplicated by incident | Paging tool, grouped |
| Distinct alerts per shift | Unique alert names fired | Alerting tool |
| Off-hours page rate | Pages between 22:00–08:00 **in the responder's local time** | Paging tool + responder TZ |
| Actionability ratio | Pages where a human action changed the outcome ÷ all pages | Requires per-page disposition tagging |
| Self-resolve rate | Alerts that cleared with no human action ÷ all fires | Alerting tool |
| MTTA | Page sent → acknowledged | Paging tool |
| TTFDA | Page sent → first diagnostic action (query, log read, command) | Shell/tool audit or manual tagging |
| Interrupt load | Fraction of business hours consumed by on-call work | Time tracking or self-report |
| Sleep interruption | Nights with ≥1 page ÷ nights on-call | Derived from off-hours pages |

**TTFDA over MTTA.** MTTA is trivially gamed by reflex acknowledgement. When MTTA is flat and
low while incident duration is long, TTFDA is the real number.

## Thresholds

| Metric | Healthy | Warning | Defect |
|--------|---------|---------|--------|
| Pages per 24h shift | ≤2 | 3–5 | >5 |
| Off-hours pages per shift | ≤1 | 2 | >2 |
| Actionability ratio | ≥80% | 50–79% | <50% |
| Self-resolve rate | <10% | 10–25% | >25% |
| MTTA | <5 min | 5–15 min | >15 min |
| Sleep interruption rate | <20% | 20–40% | >40% |
| Interrupt load (business hours) | <25% | 25–50% | >50% |
| Consecutive on-call weeks | 1 | 2 | ≥3 |
| Night burden per responder | ≤1 in 6 | 1 in 4–5 | >1 in 4 |

## Burnout Leading Indicators

These precede attrition and appear before anyone complains:

- **Escalation rate falling while page volume holds.** Responders have stopped asking for help.
- **Shift swaps concentrated in one direction.** A small group is absorbing the load.
- **Acknowledgement times improving while resolution times worsen.** Reflex acking.
- **Postmortem action items from on-call staying unclosed.** No slack to fix causes.
- **Runbook edits dropping to zero.** Nobody has capacity to improve the system they operate.
- **Same person named IC in most incidents.** Single point of human failure.
- **Rising "no action taken" dispositions.** The corpus is training people to dismiss.

Report these as system defects with owners. They are not individual resilience problems.

## Diagnosis Procedure

1. Pull 90 days of page history.
2. Rank alerts by fire count. Typically the top 5 alerts produce >50% of pages — fix those
   before touching rotation structure.
3. Split flapping (few alerts, many fires) from breadth (many alerts, few fires each) — the
   remedies are opposite.
4. Compute off-hours rate per responder in their own timezone.
5. Compute actionability. If disposition tagging does not exist, that absence is finding #1 —
   without it, no actionability claim is above `O5`.
6. Compare against thresholds and name the top three load sources by page count.
7. Only then consider rotation resizing.

**Order matters.** Resizing a rotation to absorb noise institutionalises the noise.

## Reporting

Publish monthly, to the team and to the service owner:

- Pages per shift, trend over 6 months
- Off-hours pages, per responder
- Top 5 alerts by volume, with their verdict status
- Actionability ratio, trend
- Open `KEEP (conditional)` alerts — page-worthy but undocumented
- Carry-forward register depth
- Threshold breaches, with named remediation owner

The audience for this report is whoever can authorise engineering time to fix the causes.
A health report that only reaches the on-call team is a complaint, not a control.
