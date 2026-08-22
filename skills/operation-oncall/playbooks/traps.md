<!-- operation:guidance -->
# Traps — oncall

- **Acknowledgement is not response.** Alerting tools report MTTA, and teams optimise it by
  acknowledging on reflex from a phone. Measure time-to-first-diagnostic-action instead when
  MTTA looks suspiciously flat.
- **Timezone in the paging tool is not the responder's timezone.** Off-hours ratios computed
  in UTC systematically understate night load for non-UTC teams. Convert to each responder's
  local time before judging, and state the offset used.
- **A "quiet" rotation may be a broken one.** Zero pages over a month means either genuinely
  stable service or a broken notification path. Verify delivery with a test page before
  celebrating; a silent integration is indistinguishable from silence.
- **Secondary that is never paged is not depth.** If escalation to secondary has never fired,
  the timeout is too long or the path is misconfigured. Depth you have not exercised is not depth.
- **Deleting a noisy alert deletes its history.** Export the firing history before deletion —
  it is the only evidence for why the alert existed, and postmortems will ask.
- **Flapping alerts hide in the daily count.** One alert firing 40 times in an hour and 40
  distinct alerts firing once each produce the same daily total and demand opposite fixes.
  Always report page count *and* distinct-alert count.
- **Follow-the-sun does not reduce total pages.** It redistributes them, and adds a handoff
  boundary where context is lost. Only recommend it when night load is genuinely irreducible.
