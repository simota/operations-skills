<!-- operation:deferred -->
# Operational Handover

Purpose: Transferring operational ownership, package contents, acceptance demonstration.
Read when: transferring operational ownership, package contents, acceptance demonstration
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

**Handover is complete when the receiving team can operate the service without the building
team — demonstrated, not asserted.** Document delivery is the start of handover, not the end.

## Package Contents

### 1. Service Description
- What it does, in terms the receiving team can verify against
- Who uses it, and what they cannot do when it is down
- Service tier and the impact analysis that produced it
- Architecture diagram showing every dependency, including infrastructure

### 2. Operational Interface
- How to deploy, and how to roll back
- How to scale, and where the ceiling is
- Feature flags and their meanings, including safe defaults
- Configuration: what is tunable, what the safe ranges are, what happens outside them
- Access required, and how to obtain it

### 3. Failure Modes
For each known failure mode: symptom as observed, cause, detection signal, runbook link, and
expected frequency. This is the highest-value section and the one most often reduced to a list
of past incidents.

### 4. Observability
- SLIs and SLOs, and where to see them
- Every alert: what it means, what to do, its runbook
- Dashboards, with a note on which one to open first during an incident
- Log locations, retention, and useful queries

### 5. Runbooks
Complete inventory with status. **Every runbook the tier requires must be `CURRENT`** — an
`UNVERIFIED` runbook handed over is a document the receiving team will trust and that has never
worked.

### 6. Known Issues and Debt
- Open bugs with workarounds
- Accepted risks with their review dates
- Technical debt affecting operations specifically
- **The things that are quietly held together by a person's attention.** This is the section
  that gets omitted, and it is the reason handovers fail six months later.

### 7. Contacts
- Upstream and downstream service owners
- Third-party vendor support paths and contract terms
- Escalation path for decisions the receiving team cannot make alone

## Transfer Plan

| Stage | Duration | Building team | Receiving team |
|-------|----------|---------------|----------------|
| 1. Shadow | 2–4 weeks | Operates, explains | Observes, asks, takes notes |
| 2. Supported | 2–4 weeks | Available, does not act unprompted | Operates, escalates freely |
| 3. Independent | 2–4 weeks | Reachable for genuine escalation only | Operates alone |
| 4. Complete | — | No obligation | Full ownership |

Do not compress this. A one-week handover transfers documents, not capability, and the building
team remains informally on call — often for years, invisibly, and without it being anyone's
stated job.

## Acceptance Criteria

Handover completes when **all** are demonstrated:

- [ ] The receiving team has responded to a real or simulated incident without the building team
- [ ] They have executed a deploy and a rollback independently
- [ ] They have executed at least three runbooks, including one `T3`
- [ ] They have all required access, verified by use
- [ ] They are the on-call rotation of record, receiving pages directly
- [ ] They can answer: what does this do, what breaks it, how would you know, and what would you do
- [ ] Open issues have named owners on the receiving side
- [ ] The building team's contact details are removed from alert routing

The simulated incident is the load-bearing item. Everything else can be satisfied on paper.

## Handover Anti-patterns

| Anti-pattern | Consequence |
|--------------|-------------|
| Documentation-only handover | The receiving team learns during the first real incident, badly |
| Handing over during a freeze | No changes ship, so no operational muscle is built |
| Building team stays on the escalation path "just in case" | Handover never completes; ownership stays ambiguous |
| Handing over a service with unresolved blocking findings | The receiving team inherits debt they did not choose and cannot prioritise |
| No named receiving owner | Diffuse ownership; the service decays |
| Handing over immediately after launch | The failure modes are not yet known, so the failure-mode section is empty |

## Reverse Handover

When a receiving team cannot operate a service — capacity, skills, or the service being
fundamentally unready — that is a legitimate outcome, and it should be said early rather than
absorbed silently.

State: what specifically cannot be operated, what would need to change, and who owns the
service in the meantime. **A refused handover is a better outcome than a completed one that
leaves nobody genuinely able to respond.**
