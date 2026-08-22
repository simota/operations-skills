<!-- operation:guidance -->
# Traps — incident

- **The alert stopping is not the incident ending.** Exporters die, silences expire into place,
  and scrape targets vanish — all of which look like recovery. Verify with a real user-path
  probe (synthetic transaction, manual request), not with the alert's state.
- **Rollback is not always the safe option.** Once a migration has run, rolling back the
  application into an incompatible schema is a second, worse incident. Check migration
  reversibility before treating rollback as the default.
- **Restarting destroys the evidence you will be asked for.** Heap state, in-flight requests,
  process trees, and short-retention logs vanish. Capture first; the 60 seconds it costs is
  cheaper than an unexplainable postmortem.
- **Log retention is shorter than postmortem lead time.** Debug-level logs commonly retain for
  days while postmortems are written weeks later. Export the incident window immediately, at
  `ASSESS`, not when writing the document.
- **The status page and reality drift.** A status page left green during a SEV1 is a separate
  incident with its own consequences. Assign status-page updates to the CL explicitly, or it
  is nobody's job.
- **Concurrent incidents share responders, not severity.** Two SEV2s running simultaneously
  with one responder pool is operationally a SEV1. Assess aggregate impact, not per-incident.
- **"Deploy correlation" is not causation, but it is the best first hypothesis.** Check the
  change log first — and state it as a hypothesis until reproduced.
- **Timezone-mixed timelines invert causality.** A timeline mixing JST and UTC will place the
  fix before the failure. Normalise to UTC at capture time, not at write-up time.
