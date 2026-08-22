- **Two scales, and neither is a ceremony dial.** The **service tier** (`T0`-`T3`)
  says what this service failing costs and is assigned before any requirement is
  applied; the **safety tier** (`T1`-`T4`) says what *this action* can destroy and
  is classified before the steps are designed. What scales is the depth of review
  and the number of people — never the observation rung or the approval the tier demands
- **Incident pressure changes the approver, never the tier.** A database drop is
  `T4` at 14:00 and `T4` at 03:00. What an outage may change is who is available
  to approve and how fast, and that substitution is recorded rather than assumed
- **A dialogue comes first** when a threshold is implied but unstated ("acceptable
  error rate", "enough monitoring" are numbers somebody has to choose), when the
  work sets a gate or an escalation path that binds other people, or when the
  action is `T3` or above and its approver is not identified. **State the checks
  you deliberately skipped** (`_operation/SIZING.md`)
