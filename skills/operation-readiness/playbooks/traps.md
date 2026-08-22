<!-- operation:guidance -->
# Traps — readiness

- **Tier assigned from aspiration, not impact.** Every team believes their service is critical.
  Derive the tier from what measurably happens during an hour of downtime — revenue, users
  blocked, regulatory exposure — not from how important it feels.
- **Dependency tier inversion is invisible until it fires.** Services inherit the availability
  of their weakest dependency, including the ones nobody lists: the internal auth service, the
  config store, the feature flag provider, DNS, and the CI system that ships the fix.
- **Alerts that have never fired are assumptions.** Fire each one deliberately in a test before
  certifying. The most common defect found is a routing misconfiguration — the alert works, the
  notification goes nowhere.
- **Handover completed by document delivery is not handover.** The receiving team must have
  responded to a real or simulated incident without the building team. Without that, the
  building team is still on call informally, and will be for years.
- **Capacity headroom measured on the wrong axis.** Headroom against requests per second means
  nothing when the limiting resource is database connections, a per-account rate limit, or a
  single-threaded consumer. Name the actual constraint.
- **Cost is an operational risk, not only a finance concern.** A service whose cost scales
  faster than its revenue will be capacity-limited by budget before it is limited by technology,
  and that limit arrives without a warning graph.
- **Decommissioning finds consumers you did not know about.** Batch jobs, partner integrations,
  monthly reports, and internal tools do not appear in a request dashboard sampled over a week.
  Watch for a full business cycle before shutting anything down.
- **A launch checklist becomes a formality within three launches.** Track the ratio of reviews
  producing at least one blocking finding — if it approaches zero, the checklist has stopped
  checking anything.
