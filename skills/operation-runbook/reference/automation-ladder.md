<!-- operation:deferred -->
# Automation Ladder

Purpose: Placing a procedure on the ladder, rung gates, circuit breakers, escape hatches, confidence thresholds.
Read when: placing a procedure on the ladder, rung gates, circuit breakers, escape hatches, confidence thresholds
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## The Rungs

| Rung | State | Human involvement | Gate to reach the next rung |
|------|-------|-------------------|----------------------------|
| 0 | Tribal knowledge | Everything | Write it down at all |
| 1 | Documented procedure | Reads and executes each step | Executed successfully **twice** by someone who did not write it |
| 2 | Scripted, human-invoked | Runs one command, watches | Idempotent, dry-run mode, non-zero exit on failure, logs every action |
| 3 | Self-service / one-click | Triggers it, does not watch | Preconditions checked in code, blast radius bounded in code, safe by construction |
| 4 | Automated, human-approved | Approves, then observes | Circuit breaker, escape hatch, full audit log, notification on every run |
| 5 | Fully automated | Reviews after the fact | ≥20 successful supervised runs, tier ≤ T2, verified rollback path |

## Tier Ceilings

| Tier | Maximum rung | Why |
|------|--------------|-----|
| T1 | 5 | Read-only or single-process; safe to automate fully |
| T2 | 5 | Reversible within minutes; automatable with a circuit breaker |
| T3 | 4 | Customer-visible or multi-service; a human approves each execution |
| T4 | 2 | Irreversible; scripted at most, always human-invoked |

**Skipping rungs is the dominant failure mode.** Automation built from rung 0 encodes knowledge
that was never checked against reality, and executes it faster than a human could notice.

## Rung 2 — Scripting Requirements

- **Idempotent**, or explicitly state which steps are not and guard them with state checks.
- **Dry-run mode that exercises every check the real run does** — including permission checks.
  A dry-run that skips checks succeeds where the real run fails halfway through.
- **Non-zero exit on any failure.** Scripts that log an error and continue produce partial
  application, which is worse than failing.
- **Structured logging** of every action taken, with timestamps, to durable storage.
- **No silent defaults.** An unset variable aborts; it does not fall back to production.
- **Explicit environment targeting.** The script names its target and refuses to run if the
  current context does not match.

## Rung 4 — Automation Gates

Required before any automated execution:

```yaml
automation_gate:
  preconditions:      # checked in code before acting; failure = no action + notify
    - "<condition>"
  blast_radius:
    max_instances: <n>          # refuses to act on more than this
    max_percent_of_fleet: <n>
    environments: [<list>]      # explicit allowlist
  circuit_breaker:
    max_consecutive_failures: 3   # a success resets the count to zero
    window: "1h"                  # failures older than this age out
    on_trip: "stop, page primary, do not retry until a human clears the breaker"
    hard_stop: "<condition that aborts immediately, before 3 — e.g. the action itself errored
                in a way that indicates the precondition check was wrong>"
  escape_hatch:
    disable: "<command or flag that stops it immediately>"
    owner_notified: true
  audit:
    log_destination: "<durable store>"
    notify_on_every_run: "<channel>"
  verification:
    post_action_check: "<what proves it worked>"
    on_verification_failure: "revert and escalate"
```

### Circuit Breaker

Non-negotiable. Automation that retries against a broken system amplifies failure — restart
loops, redeploy loops, and scale-up loops turn degradation into outage.

Rule: **three consecutive *failed* attempts within the window, then stop, page a human, and do
not retry until a human clears the breaker.** A successful run resets the count to zero;
failures age out of the window. Some conditions warrant an immediate stop before the third
attempt — declare them as `hard_stop`, typically "the precondition check was wrong" cases where
retrying cannot help. The trip itself is an event worth alerting on: automation tripping its
breaker means the assumption behind it no longer holds.

### Escape Hatch

Every automated procedure has a documented way for a human to stop it **mid-flight**, and that
mechanism is tested. A kill switch that has never been exercised is a hypothesis.

## Rung 5 — Full Autonomy

Only reachable with all of:

- ≥20 successful supervised executions with no manual correction
- Tier ≤ T2 (reversible within minutes)
- Verified rollback path, exercised
- Post-action verification in code, with automatic revert on failure
- Complete audit trail
- Reviewed monthly for drift — the underlying system changes even when the automation does not

## What Not to Automate

- **The *triggering* of `T4` actions.** Irreversible mutation, deletion, credential
  revocation, restore-from-backup. Script them (rung 2) — a script a human invokes is safer
  than the same steps typed under pressure — but the decision to run stays human. Note that
  the tier follows reversibility, not the action's name: a backfill with an exercised
  down-path is not `T4` (`_operation/SAFETY_TIERS.md`).
- **Procedures whose trigger conditions are ambiguous.** Automation cannot exercise judgement
  about whether the symptom matches; if a human must decide "is this that case?", keep the human.
- **Rarely-executed procedures — unless a rehearsal cadence keeps them warm.** Below roughly a
  dozen executions a year, automation is stale when it fires and nobody trusts it, so rung 2 is
  usually the right ceiling. The exception is a high-risk, unambiguous procedure (DR failover,
  restore) where the *manual* path is more dangerous than the automated one: there, automate but
  bind it to a scheduled rehearsal, and treat a missed rehearsal as expiring the automation.
- **Procedures nobody currently understands.** Automating a procedure to avoid learning it
  guarantees nobody can debug it when it breaks.
- **Novel failures.** Automation handles known patterns. The value of a human on-call is
  precisely the unknown case.

## Automating the Decision, Not Just the Keystrokes

Rung 2 automation typically saves the *typing*, which is rarely the expensive part. The
expensive parts are deciding **whether** this is the right procedure and **verifying** it worked.

Automate in this order:
1. **Verification** — automated post-checks catch partial application; highest value, lowest risk.
2. **Precondition checking** — prevents the wrong runbook being run against the wrong state.
3. **Execution** — the keystrokes.
4. **Triggering** — the decision to act at all; highest risk, do last.

Teams reliably do this backwards, automating triggering first and verification never.
