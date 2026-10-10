- **Cite the rung inline on every claim** (`_operation/CONTRACT.md`): `O1`
  observed · `O2` reproduced · `O3` documented · `O4` reported · `O5` inferred.
  **A root cause requires `O2`**, or its mechanism observed where reproducing is
  unsafe; mitigation may proceed on `O1`. `payment-api 5xx rate 12% [O1: panel 44,
  05:02Z]` beats "payments are erroring", and a missing rung is a stated gap
- **No invented telemetry.** Never state a metric value, alert name, dashboard or
  runbook path that was not read from the repo, the tooling, or the user. If a
  value is needed and absent, say what to query and where
- **Report `status`**: `DONE` (every claim runged, every action tiered, zero
  `UNVERIFIED`) / `PARTIAL` / `BLOCKED` (say what was tried)
- **Every residual is `BLOCKED` / `OUT-OF-SCOPE` / `DEFERRED` / `UNVERIFIED`** and
  appears in the handoff's `open`. `UNVERIFIED` is the class this domain turns on:
  **an untested procedure and a tested one are indistinguishable until the night
  you need it**
- **Never omit the sweep** — markers against `open`, claims against claims runged:
  `swept, 0 markers; 14 claims / 14 runged`
