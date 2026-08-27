<!-- operation:deferred -->
# Rollback Playbook

Purpose: Verifying reversibility, expand-contract migration sequencing, point of no return, post-deploy verification.
Read when: verifying reversibility, expand-contract migration sequencing, point of no return, post-deploy verification
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — no automated check.

## Reversibility Checklist

Run before approving any change. Any unchecked box moves reversibility to score 5.

- [ ] The previous artifact version is still available and deployable
- [ ] No schema migration ran, **or** the migration is backwards-compatible with the previous version
- [ ] The new version writes no data the old version cannot read
- [ ] Message, event, and queue formats are compatible in both directions
- [ ] Cache key formats and serialisation are unchanged, or the cache can be flushed safely
- [ ] No dependent service has already been upgraded to require the new behaviour
- [ ] Feature flags introduced by this change have a defined revert state
- [ ] The rollback procedure has been exercised within 90 days
- [ ] Rollback duration is known and acceptable given the impact rate
- [ ] Rolling back does not lose data written during the forward window

## Rollback ≠ Redeploying the Old Version

Redeploying the previous artifact does not undo:

| Side effect | Persists after redeploy | Mitigation |
|-------------|------------------------|------------|
| Schema migration applied | Yes | Backwards-compatible migrations only, or a tested down-migration |
| Data written in the new format | Yes | Dual-format read support in the old version, or a repair job |
| Messages published in the new format | Yes | Consumers tolerate both formats before producers change |
| Cache entries in the new format | Yes | Version the cache keys; old version misses rather than misreads |
| Feature flags flipped | Yes | Revert flags explicitly as part of rollback |
| Downstream state changed by the new behaviour | Yes | Enumerate per change; often requires a repair procedure |
| Third-party side effects (webhooks, emails sent, charges) | Yes | Cannot be rolled back — this is a point of no return |

Enumerate side effects for every change. **The rollback plan covers the side effects, not just
the artifact version.**

## Point of No Return

Name it for every change. It is one of the highest-value outputs of a change review, and it is
usually **earlier** than people expect.

| Change type | Typical point of no return |
|-------------|---------------------------|
| Schema migration | When the contract phase drops the old column — but often earlier, at first new-format write |
| Data format change | First write in the new format that a consumer has read |
| Message format change | First message consumed by a consumer that cannot handle the old format |
| Credential rotation | When the old credential is revoked |
| Third-party side effect | The moment the external call succeeds |
| Cache format change | When the cache is warm enough that a cold restart is itself an incident |
| Feature flag rollout | Usually NONE — this is why flags are valuable |

For each change, state either the moment, or `NONE` explicitly.

## Expand → Migrate → Contract

The only reliable pattern for schema and format changes. **Each phase ships separately.**

| Phase | Action | Reversible? | Tier |
|-------|--------|-------------|------|
| **Expand** | Add the new column/field/format. Both old and new coexist. Code writes old, reads old | Yes — the addition is unused | T2 |
| **Migrate** | Code writes both, reads old. Then backfill. Then read new, still write both | Yes — old data is still current | T2–T3 |
| **Contract** | Stop writing old. Later, drop the old column | **No** — this is the point of no return | T4 |

Rules:
- Never ship expand and contract together. Combining them removes the rollback path silently,
  and the change will still be labelled low-risk because the diff looks small.
- Leave a **soak period** between phases — at minimum one full business cycle, so that weekly
  batch jobs and monthly reports exercise the new state.
- The contract phase is a separate, explicitly approved `T4` change, executed only after
  confirming no reads of the old field remain. Verify with instrumentation, not with grep.
- Backfills are their own change, with their own rate limiting, progress tracking, and abort path.

## Post-Deploy Verification

Deploy success means the artifact is running. It does not mean it works.

Verify in order:

1. **User-path probe** — a real transaction through the real path. The only `O1` evidence.
2. **SLI check** — the user-facing indicator at baseline, not merely "not alerting".
3. **Error budget** — burn rate unchanged.
4. **Downstream health** — dependents unaffected.
5. **Async paths** — queues, jobs, webhooks, scheduled tasks. These are where post-deploy
   failures hide, because they do not show up in request metrics.
6. **Data correctness** — spot-check records written since the deploy.
7. **Resource trend** — memory and connection counts over the bake window; leaks do not appear
   in the first five minutes.

## When Rollback Is Not Available

State it plainly and plan accordingly:

- Add extra rollout stages with smaller populations and longer bakes.
- Require a **repair procedure** instead of a rollback — written, tested, and owned before the
  change ships.
- Increase coverage for the window (`operation-oncall`).
- Consider whether the change can be restructured to be reversible. Usually it can, at the cost
  of an extra phase; that cost is almost always worth paying.
- Never record a change as low risk because the diff is small. Reversibility is independent of
  diff size — a one-line migration is the least reversible change on this page.

## Rollback Execution

- Rollback is itself a change: it needs a watcher, verification, and a record.
- **Disable the deploy trigger before rolling back.** A CD pipeline that redeploys on a health
  check produces version flapping while the rollback is in flight.
- Revert feature flags alongside the artifact, in the same operation.
- Verify with the user-path probe, exactly as for a forward deploy.
- If rollback does not restore service, **do not conclude the change was innocent.** Three
  readings are live, and they need different responses:
  | Reading | Check |
  |---------|-------|
  | The rollback was incomplete | Did every side effect revert? Flags, migrations, cache formats, queued messages (see the table above) |
  | The change caused a persistent effect | Is there state written during the forward window that the old version is now tripping over? |
  | The change was not the cause | Is there an independent trigger in the same window — a dependency, a traffic shift, an expiry? |
  Work the first two before adopting the third. Concluding "not the change" while a partial
  revert is still in place sends responders hunting a fresh hypothesis with the real cause
  still in production.
