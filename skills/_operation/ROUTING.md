<!-- operation:guidance -->
# Routing Map

Five skills cover the Day-2 operations lifecycle. Pick by the question being asked, not by
the system being discussed.

**Boundaries are defined in `registry/capabilities.yaml`, not here and not in any skill's
description.** Each entry carries what a skill does, what it does not (`not:`, with where
that work goes instead), and the words that select it. Writing an exclusion into a
description makes every skill added rewrite its neighbours; keeping it in one file makes an
addition cost O(1). The table below is a reading of that file, not a second copy of it.

The chains that recur are in `registry/routes.yaml`, with their control structure. Where a
stage repeats until a condition holds, the entry carries the stopping condition, the judge,
and a hard cycle limit — and **the team that built a thing may not certify it**.

| The question | Skill |
|--------------|-------|
| "Who gets paged, when, and is this alert worth waking someone for?" | `operation-oncall` |
| "Something is broken right now — what do we do?" | `operation-incident` |
| "How is this procedure performed, and can it be automated?" | `operation-runbook` |
| "Is it safe to ship this, and how do we undo it?" | `operation-change` |
| "Is this service ready to be operated, and by whom?" | `operation-readiness` |

## Disambiguation

| Ambiguous request | Goes to | Because |
|-------------------|---------|---------|
| "Reduce our alert noise" | `operation-oncall` | Alert quality is rotation health, not incident work |
| "Write a postmortem" | `operation-incident` | Postmortem is the closing phase of incident response |
| "Automate this manual task" | `operation-runbook` | Toil accounting and the automation ladder live there |
| "How should this deploy roll out, and how do we undo it?" | `operation-change` | Rollout strategy and rollback are change concerns; building the CI system itself is out of scope |
| "This deploy broke prod" | `operation-incident` | Active user impact outranks change process |
| "Should we roll back or fix forward?" | `operation-incident` | Mitigation decision during impact |
| "What must be true before launch?" | `operation-readiness` | PRR gate |
| "Hand this service to the ops team" | `operation-readiness` | Handover package |
| "Our on-call is burning out" | `operation-oncall` | Rotation health |
| "Cut our cloud bill" | `operation-readiness` | Capacity and cost review; not an incident |

## Out of Scope for This Repo

These are adjacent and belong elsewhere:

- Writing the application fix itself — an implementation task, not an operations task.
- Designing SLIs/SLOs and instrumentation from scratch — observability engineering.
  `operation-*` skills consume SLOs; they do not define the telemetry pipeline.
- Provisioning infrastructure or authoring IaC modules.
- Security vulnerability analysis and threat modelling.
- Product prioritisation of the resulting action items.

When a request is primarily one of the above, say so and name what `operation-*` can still
contribute (usually: the runbook, the rollout plan, or the readiness gate around it).
