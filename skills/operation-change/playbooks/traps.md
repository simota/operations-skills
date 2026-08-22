<!-- operation:guidance -->
# Traps — change

- **Rollback and roll-forward-to-previous-version are not the same thing.** Redeploying the old
  artifact does not undo the migration it ran, the messages it published, the cache entries it
  wrote, or the flags it flipped. Enumerate the side effects, not just the artifact version.
- **The point of no return is usually earlier than people think.** It is frequently the first
  write in the new format, not the contract migration — once a consumer has read the new format,
  the old version cannot serve those records.
- **Canary populations are rarely representative.** Routing 1% by hash gives you 1% of typical
  traffic and 0% of the enterprise customer whose payload is the one that breaks. State what the
  canary population does *not* cover.
- **Bake time must exceed the slowest feedback loop.** If a bug surfaces through a batch job that
  runs hourly, a 10-minute bake proves nothing. Set bake times from the feedback loop, not from
  impatience.
- **Feature flags are changes too.** A flag flip is a production change with no deploy record,
  no review, and often no rollback plan. Flag changes belong in the change log; incidents caused
  by untracked flag flips are near-impossible to correlate.
- **Freeze exits concentrate risk.** The first day after a freeze ships a batch equal to the
  freeze's length, with everyone assuming the others tested. Plan a staged exit, not a floodgate.
- **Approval rubber-stamps are detectable.** An approval gate with a >99% approval rate and a
  median approval time under two minutes is a logging mechanism, not a control. Either give the
  approver what they need to say no, or remove the gate.
- **Automated rollback can fight automated deploy.** A CD pipeline that redeploys on a health
  check while a rollback is in flight produces version flapping. Ensure rollback disables the
  deploy trigger first.
