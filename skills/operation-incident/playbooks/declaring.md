<!-- operation:guidance -->
# Live State Block, Declaration Criteria

## Live State Block

While an incident is active, this is the record, kept current where the responders read it —
not what every response repeats (`_operation/REPORT.md`). A response opens with the `IMPACT`
line and adds only the fields the reader must act on now.

```
INCIDENT <id> | SEV<n> | <DECLARED|MITIGATING|MONITORING|RESOLVED>
IMPACT:   <who is experiencing what, right now>
SINCE:    <UTC timestamp> (<local>) — <elapsed>
IC:       <name>   OL: <name>   CL: <name>   Scribe: <name>
NOW:      <the single action in progress>
NEXT:     <the next decision and when it is due>
COMMS:    last <time> | next <time>
```

An unfilled field is written as `UNASSIGNED` or `UNKNOWN`, never omitted. `IC: UNASSIGNED`
on a SEV1 is the most important line on the screen, and goes into every response until it is filled.

## Declaration Criteria

Declare when **any** holds — the severity is decided afterwards:

- A user-facing SLO is burning at a rate that exhausts the budget in under 24 hours.
- Any customer has reported impact that reproduces.
- Data integrity, durability, or confidentiality is in question.
- The responder does not know what is happening and impact is plausible.
- Two or more teams are needed to resolve it.
- Anyone asks "should we declare?" — the question is the answer.

**Downgrading and closing early is free.** Make this explicit in the incident record so the
next responder declares without hesitating.
