<!-- operation:contract -->
# Handoff Contract

`operation-*` skills chain. A handoff carries state forward without forcing the next skill
to re-derive it. **It is the record, not the report**: what a person reads is a bounded view
over it (`_operation/REPORT.md`), never this schema rendered field by field.

## Schema

```yaml
OPERATION_HANDOFF:
  from: operation-[name]
  to: operation-[name] | DONE
  reason: "[why this skill is next — one line]"
  state:
    subject: "[service, change, or incident identifier]"
    phase: "[phase the sending skill completed]"
    service_tier: T0 | T1 | T2 | T3
    safety_tier: T1 | T2 | T3 | T4
  carried:
    - "[fact the receiving skill would otherwise re-derive, with observation rung]"
  artifacts:
    - "[path or URL]"
  open:
    - blocking: true | false
      question: "[what is unresolved]"
  do_not_repeat:
    - "[work already done — the receiving skill must not redo it]"
```

## Canonical Chains

| Chain | When |
|-------|------|
| `operation-readiness` → `operation-runbook` → `operation-oncall` | New service entering production |
| `operation-oncall` → `operation-incident` | A page escalates into a declared incident |
| `operation-incident` → `operation-runbook` | Postmortem produced a repeatable procedure |
| `operation-incident` → `operation-change` | Fix requires a controlled rollout |
| `operation-change` → `operation-incident` | A change caused impact; rollback is now incident work |
| `operation-runbook` → `operation-oncall` | New runbook must be linked from its alert |
| `operation-incident` → `operation-readiness` (`systemic`) | A component has appeared in ≥3 postmortems |
| `operation-oncall` → `operation-change` | A change's risk window can or cannot be staffed |

## Rules

- **`do_not_repeat` is binding.** The receiving skill treats those items as settled unless
  it finds contradicting `O1` evidence, in which case it says so explicitly.
- **Never hand off mid-mitigation.** `operation-incident` holds the baton until user-visible
  impact ends. Handoff happens at phase boundaries, not inside them.
- **A handoff with no `carried` block is a re-start, not a handoff.** Fill it or don't chain.
