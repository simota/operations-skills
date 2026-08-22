<!-- operation:guidance -->
# Traps — runbook

- **Idempotency is claimed far more often than it holds.** "Apply the config" is idempotent;
  "increment the counter", "append to the file", "create the resource" are not. Test by running
  twice and diffing the resulting state, not by reading the code.
- **The dry run and the real run take different code paths.** A dry-run that skips the
  permission check succeeds where the real run will fail on step 9, halfway through. Dry-run
  must exercise every check the real run does.
- **Copy-pasted commands carry invisible characters.** Runbooks rendered in rich text turn
  hyphens into en-dashes and quotes into smart quotes, producing commands that fail obscurely
  at 3 a.m. Keep commands in fenced code blocks, always.
- **A runbook drifts silently while the system changes.** The document does not break when the
  CLI flag is renamed. Freshness is measured by last *execution*, never by last *edit* — an
  edited-yesterday runbook that has not run in a year is more dangerous than an honest old one.
- **Runbooks written during an incident are optimistic.** They record what worked once, under
  one set of conditions, omitting the four things that were tried first. Always revisit an
  incident-authored runbook when calm.
- **Automation that retries a broken system amplifies the failure.** Restart loops, re-deploy
  loops, and scale-up loops against a hard failure convert a degradation into an outage. Three
  attempts, then stop and escalate.
- **"Escalate to the team" is not a final step.** It hides an unfinished runbook. Name who,
  through which channel, with what context attached.
- **A step whose output is "check the dashboard" is not verifiable.** Name the panel, the metric,
  the expected value, and the tolerance.
