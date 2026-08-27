<!-- operation:deferred -->
# Incident Command Structure

Purpose: Assigning IC/OL/CL/Scribe, authority boundaries, command transfer, war-room discipline.
Read when: assigning IC/OL/CL/Scribe, authority boundaries, command transfer, war-room discipline
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

Adapted from incident command systems used in emergency response: the point is that authority
is explicit and the commander does not perform the work.

## Roles

| Role | Owns | Explicitly does not |
|------|------|---------------------|
| **IC** (Incident Commander) | Decisions, priorities, delegation, severity, all-clear | Touch a terminal, debug, write the fix |
| **OL** (Operations Lead) | Executing mitigations, hands on the system | Decide scope, severity, or comms |
| **CL** (Communications Lead) | Internal updates, customer notice, status page | Make technical calls |
| **Scribe** | Real-time timeline with UTC timestamps and evidence links | Anything else — this is a full-time role |
| **SME** | Domain expertise on request | Act without OL/IC direction |

### Why the IC does not debug

An IC in a terminal loses the room: they stop tracking elapsed time, stop noticing the comms
cadence slipping, and stop hearing the SME who found the answer. If the only person who can
debug is the IC, hand off **command**, not the debugging.

## Scaling by Severity

| Severity | Minimum structure |
|----------|-------------------|
| SEV1 | IC + OL + CL + Scribe, four distinct people |
| SEV2 | IC + OL + Scribe; IC may also carry CL |
| SEV3 | Single responder; no formal roles |
| SEV4 | Ticket |

If a SEV1 cannot staff four roles, that is escalated as a coverage failure at the same time
as the incident is worked — do not quietly collapse roles and proceed.

## Command Transfer

Explicit, verbal or written, acknowledged. Never implicit.

```
IC TRANSFER
From: <name>   To: <name>   At: <UTC> (<local>)
Current state:  <impact, one line>
Actions in flight: <what is running, who is running it>
Decisions made:  <what has been ruled in and out, and why>
Decision pending: <the next call and when it is due>
Comms:          last <time>, next <time>, audiences notified <list>
Constraints:    <what the incoming IC must not do without approval>
Accepted by: <incoming IC> at <UTC>
```

Transfer triggers: shift boundary, IC fatigue (mandatory after ~4 hours on SEV1), the IC
becoming the only person who can execute the fix, or escalation to a more experienced IC.

**An incident is never left without an IC**, including across a handoff minute.

## War Room Discipline

- **One channel of record.** Side conversations in DMs mean the Scribe misses the decision
  that mattered. State this at the start.
- **Voice for coordination, text for record.** Every decision made on a call is echoed in the
  channel by the Scribe with a timestamp.
- **The IC calls for status on a fixed rhythm** (every 15 min at SEV1): each active responder
  gives one line — what they are doing, what they have ruled out, what they need.
- **Observers stay silent.** Explicitly designate a read-only audience. A war room where
  executives ask for updates directly consumes the IC; the CL owns them instead.
- **One action at a time on the same subsystem.** Two people changing the same thing produces
  a system state nobody can reason about, and a timeline nobody can reconstruct.

## Scribe Protocol

The Scribe captures, in real time:

| What | Format |
|------|--------|
| Every action taken | `HH:MM:SSZ <who> <action> — <result>` |
| Every decision | `HH:MM:SSZ DECISION: <what> — because <why> — <who>` |
| Every hypothesis and its fate | `HH:MM:SSZ HYPOTHESIS: <what> → CONFIRMED/REFUTED at HH:MM` |
| Every comms send | `HH:MM:SSZ COMMS: <audience> — <link>` |
| Evidence links | Permalink to log query, dashboard snapshot, screenshot |
| Severity changes | With deciding dimension |

**Dashboards are ephemeral.** Screenshot them; a Grafana link with a relative time range shows
different data next week. Capture absolute-time permalinks or images.

## Decision Log

Separate from the timeline, and the highest-value postmortem input:

```
DECISION <n> at <UTC>
Made by:      <IC>
Options:      <A / B / C>
Chosen:       <B>
Because:      <reasoning available AT THE TIME>
Known unknowns: <what was not known when deciding>
Reversal:     <how to undo, or NONE>
```

Recording "reasoning available at the time" is what makes the postmortem blameless: it lets
reviewers evaluate the decision against the information that existed, not against hindsight.
