<!-- operation:contract -->
# EXPIRY — proof of an undo, and the date it stops counting

Binding on every `operation-*` skill. Operations rests on a class of claim that
is never exercised in normal running: *we can roll this back*, *we can restore
from that*, *this runbook works*, *that page reaches someone*. **Each of them
carries a state and an expiry, and neither is optional.**

## The failure this prevents

An untested rollback is byte-for-byte identical to a working one until the night
it is needed. Nothing in normal operation distinguishes them, so nothing in
normal operation corrects the belief. The document says the procedure exists;
the belief that it works was never separately acquired.

Worse, proof decays silently. A restore proved a year ago, against a schema
since migrated, reads in the record exactly like one proved on Tuesday. **A date
by itself has no failure mode** — it records that somebody once looked, and an
unchecked claim that reads like a checked one is the whole problem.

## The five states

Every undo path, restore path, runbook path, failover and escalation path is
in exactly one.

| State | Means | May a plan depend on it? |
|---|---|---|
| `proved` | Executed end to end, in an environment that matters, on a named date, by a named person or job | Yes |
| `simulated` | Executed only in a lower environment, or with the destructive step stubbed | Only with the gap stated in the same sentence |
| `stale` | Was `proved`, and its expiry has passed | No — treat as `untested` until re-run |
| `untested` | Never executed | No. It is a plan, not a capability |
| `unprovable` | Cannot be executed without unacceptable cost or risk | Only with a named compensating control and its owner |

`untested` and `stale` are both `UNVERIFIED` in the completion contract. They
are kept apart here because they fail differently: one was never built, the
other rotted, and only the second gives a false sense of coverage.

## What sets the expiry

Two clocks, and **whichever fires first wins**:

- **An interval**, chosen from how fast this system changes, not from a round
  number. Say why the interval is what it is
- **A named surface** — the schema, the deploy pipeline, the IAM boundary, the
  on-call roster. **A change to it expires the proof immediately**, whatever the
  interval says. Naming the surface is what gives the date a failure mode

The record carries both: `proved 2026-03-14, expires 2026-09-14 or on any
change to the backup schema`.

## What upgrades a state

**Execution, and nothing else.** Re-reading the runbook, re-reviewing the
Terraform, a colleague's recollection that it worked last time — none of these
move a state. A dry run moves `untested` to `simulated`, never to `proved`.

Downgrades need no ceremony: the interval passing, or the named surface
changing, does it, and the record is updated where it stands.

## Boundary cases

- **A rollback exercised by a real incident is `proved`** — a production
  execution is the strongest kind. Record the date and what was actually run
- **A partially executed procedure is `untested` for every step after the one
  that stopped.** Steps are not proved in bulk
- **A runbook whose steps were performed by hand while the automation was
  broken** proves the steps, not the runbook. The path that will be taken next
  time is the one that must be proved
- **`unprovable` is a real answer**, not a failure of nerve — restoring the
  production database is not exercised for practice. It obliges a compensating
  control, its owner, and the smallest part that *can* be proved, proved
- **An escalation path is proved by a page that reached a human**, not by the
  policy being correct in the tool
