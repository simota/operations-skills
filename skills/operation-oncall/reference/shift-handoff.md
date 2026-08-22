<!-- operation:deferred -->
# Shift Handoff

Purpose: Handoff template, carry-forward register, degradation tracking across shifts.
Read when: handoff template, carry-forward register, degradation tracking across shifts
Verified: 2026-08-21 — no automated check.

A handoff is a deliverable. Its quality metric: **did the incoming shift have to re-derive
anything?** If yes, the handoff failed.

## Handoff Template

```markdown
# On-call Handoff — <team> — <YYYY-MM-DD HH:MM TZ>
Outgoing: <name>   Incoming: <name>

## 1. Current state
- Active incidents: <ID, severity, current status, IC> | none
- Degraded but not incident: <what, since when, why not escalated>
- Ongoing mitigations in place: <what, expiry, who owns removal>

## 2. Active silences / suppressions
| Alert | Silenced until | Reason | Owner |

## 3. Changes in flight
- Deploys in progress or scheduled during your shift
- Freeze windows starting/ending
- Migrations, backfills, or long-running jobs and their expected completion

## 4. Watch items
- <signal to watch, threshold, what to do if it crosses>

## 5. Known-noisy alerts this shift
- <alert> — expected to fire, known cause, action: <none | X>

## 6. Carried-forward items
| Item | Age (shifts) | Owner | Next step |

## 7. Anything you would want to know at 03:00
<free text — the most valuable field; do not leave blank>
```

## Rules

- **Handoff happens live** — synchronous, 10–15 minutes, both parties present. A document
  dropped in a channel is a record, not a handoff.
- **Never hand off mid-incident.** If an incident is active, either the outgoing responder
  stays until a stable state, or a formal IC transfer occurs with the incoming responder
  briefed by the IC — not by the outgoing responder alone.
- **Silences are handed off explicitly.** An inherited silence nobody mentioned is how a
  suppressed alert becomes a missed outage.
- **Empty is a valid handoff**, and it should be said out loud: "nothing active, no silences,
  no changes in flight." Silence is ambiguous; explicit nothing is not.

## Carry-Forward Register

Items that survive a shift boundary accumulate invisibly. Track age in shifts:

| Age | Action |
|-----|--------|
| 1–2 shifts | Normal carry-forward |
| 3–5 shifts | Assign a named owner outside the rotation; it is no longer on-call work |
| >5 shifts | Escalate to the service owner as unowned operational debt |

An item nobody will own after five handoffs is either not important or is being ignored.
Both need a decision, and on-call is the wrong place to make it repeatedly.

## Degradation Register

Distinct from incidents: conditions that are wrong but tolerated. Each entry carries what is
degraded, since when, the accepted user impact, why it is not an incident, and the review date.

Without this register, chronic degradation becomes the baseline and the team stops seeing it.
Review the register monthly; any entry older than 30 days is either fixed, formally accepted
with an owner, or escalated.

## Handoff Quality Signals

| Signal | Meaning |
|--------|---------|
| Incoming shift asks questions answerable from the doc | Template not being filled |
| Section 7 routinely blank | Handoff is being treated as a form |
| Incidents re-diagnosed after handoff | Context lost at the boundary |
| Silences discovered rather than handed over | Section 2 skipped |
| Carry-forward register only grows | No owner-assignment discipline |
