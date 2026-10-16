- **Every undo, restore, runbook, failover and escalation path carries a state and
  an expiry.** `proved` · `simulated` · `stale` · `untested` · `unprovable` — with
  the date it was executed, and both clocks that end it: an interval with its
  reason, and the named surface whose change voids it immediately. **Only
  execution upgrades a state**; a dry run reaches `simulated`, never `proved`.
  `stale`, `untested`, `simulated` without its gap and `unprovable` without its control are
  `UNVERIFIED` (`_operation/EXPIRY.md`)
