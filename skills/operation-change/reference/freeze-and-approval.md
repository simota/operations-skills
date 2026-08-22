<!-- operation:deferred -->
# Freeze Windows and Approval

Purpose: Freeze windows, exemptions, emergency change handling, approval design, rubber-stamp detection.
Read when: freeze windows, exemptions, emergency change handling, approval design, rubber-stamp detection
Verified: 2026-08-21 — no automated check.

## Freeze Design

A freeze refuses `Normal` changes for a defined window. It does not — ever — refuse `Emergency`
changes.

| Element | Requirement |
|---------|-------------|
| Scope | Which services, which environments. A blanket organisation-wide freeze is rarely justified |
| Window | Explicit start and end, with timezone |
| Rationale | Named. "It's December" is not a rationale; "thin coverage over the holiday period plus peak retail traffic" is |
| Exemptions | Criteria stated in advance, not decided ad hoc under pressure |
| Emergency path | Explicit, and tested before the freeze begins |
| Exit plan | How the accumulated backlog ships afterwards |

## Justified vs Unjustified Freezes

| Justified | Unjustified |
|-----------|-------------|
| Coverage genuinely reduced (holidays, offsite) | "Changes are risky" — fix the change process instead |
| Peak business period where impact cost is exceptionally high | Blanket year-end freeze with no traffic rationale |
| A dependency is mid-migration and cannot absorb change | Compensating for a lack of tests |
| Regulatory or audit window | Punishment after an incident |

**A permanent or near-permanent freeze is a symptom.** It means the team does not trust its
change process, and freezing does not repair that trust — it defers the failures into a larger,
riskier batch.

## Exemption Criteria

Stated in advance:

- Security patches above a severity threshold
- Fixes for active or imminent customer impact
- Changes that reduce risk (adding monitoring, adding a flag, improving a rollback path)
- Changes with a risk score below a threshold and a verified rollback
- Time-critical external deadlines (certificate expiry, partner cutover)

Every exemption is recorded with who approved it. An unrecorded exemption is indistinguishable
from a freeze violation, and it destroys the freeze's meaning for everyone else.

## Freeze Exit

The most dangerous moment of the whole freeze.

| Risk | Mitigation |
|------|------------|
| A batch equal to the freeze length ships at once | Staged exit over several days, ordered by risk score |
| Changes were written weeks ago; context has faded | Require re-review of anything older than the freeze |
| Everyone assumes someone else tested against current main | Rebase and re-run integration tests before shipping |
| Coverage is still thin on day one back | Schedule the exit after full coverage resumes, not on the last day of the freeze |
| Interacting changes accumulated | Sequence by dependency; do not ship coupled changes on the same day |

Plan the exit **when the freeze is declared**, not when it ends.

## Approval Design

Approval is a control only when the approver can meaningfully say no. Otherwise it is a logging
mechanism with extra latency.

| Risk score | Approval |
|------------|----------|
| 5–9 (`Standard`) | None; automatic log |
| 10–15 | Service owner, asynchronous |
| 16–20 | Service owner + a second reviewer with domain knowledge |
| 21–25 | Explicit review with a rollout plan; split recommendation first |
| Emergency | IC during the incident; post-review within 5 business days |

### What an Approver Needs

An approval request without these cannot be evaluated, and will be rubber-stamped:

- What is changing, in one line
- Risk score with the deciding dimension
- Rollback procedure and its last-exercised date
- Point of no return
- Abort trigger and watcher
- What was tested and what was not

### Rubber-Stamp Detection

Measurable signals that a gate is not a control:

| Signal | Threshold |
|--------|-----------|
| Approval rate | >99% over 100+ changes |
| Median time to approve | <2 minutes for non-`Standard` changes |
| Approvals outside working hours | High share, suggesting reflex approval |
| Approver has never rejected | Any approver with zero rejections in a year |
| Approval requests lacking rollback information | Any — the gate is not enforcing its own inputs |

Response: either give the approver the information and authority to say no, or remove the gate
and rely on progressive rollout instead. **A gate that manufactures assurance without providing
it is worse than no gate** — it produces confidence that suppresses other controls.

## Emergency Changes

- Never blocked by a freeze. A freeze that blocks incident response is misconfigured; say so.
- Approved by the IC during an incident — no separate *change* approval is sought mid-impact.
  This replaces the change-approval path, **not** the safety-tier gate: a `T4` emergency change
  still requires the IC plus a second responder (`_operation/SAFETY_TIERS.md` § Escalation During
  Incidents). Incident pressure changes who approves, never whether.
- Recorded **after**, with the same fields as any change record, plus what was skipped and why.
- Reviewed within 5 business days: was the emergency classification correct? Did skipping the
  normal path cause any harm? Should a `Standard` change exist to cover this case next time?
- **Emergency change frequency is a metric.** A team with a high share of emergency changes has
  a change process people are routing around, not an unusual number of emergencies.
