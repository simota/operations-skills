<!-- operation:guidance -->
# Live State Block, Declaration Criteria

## Live State Block

While an incident is active, every response opens with this. Nothing precedes it.

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
on a SEV1 is the most important line on the screen.

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
