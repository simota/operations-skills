# operations-skills

Five agent skills covering Day-2 operations, the contracts they share, and the
budgets that keep the set from growing into something nobody can route through.

**None of these skills operate the system.** The change is made, the incident
mitigated, and the runbook executed by people; these produce the decision, the
procedure, and the record.

| Skill | Answers | Class |
|---|---|---|
| [`operation-incident`](skills/operation-incident/SKILL.md) | Something is broken right now — what do we do? | advise |
| [`operation-change`](skills/operation-change/SKILL.md) | Is it safe to ship this, and how do we undo it? | advise |
| [`operation-oncall`](skills/operation-oncall/SKILL.md) | Who gets paged, when, and is this worth waking someone for? | advise |
| [`operation-runbook`](skills/operation-runbook/SKILL.md) | How is this performed, and can it be automated? | advise |
| [`operation-readiness`](skills/operation-readiness/SKILL.md) | Is this service fit to run, and by whom? | review — never edits |

## The four ideas the set is built on

**Operations runs on claims about a system nobody can see directly, so every
claim is ranked.** `O1` observed · `O2` reproduced · `O3` documented · `O4`
reported · `O5` inferred. **A root cause requires `O2`**; mitigation may proceed
on `O1`. `O4` never survives a postmortem unchallenged, because human
recollection of timing is systematically wrong. A missing rung is stated as a
gap, never left blank — and no metric, alert, dashboard or runbook path is
stated that was not read.

**Two scales, and neither is a ceremony dial.** The service tier says what the
service failing costs; the safety tier says what *this action* can destroy. What
scales is the depth of review and the number of people involved — never the
observation rung or the approval the tier demands. **Incident pressure changes the
approver, never the tier.**

**`UNVERIFIED` is the residual class this domain turns on.** An untested
rollback, an unexecuted runbook, a mitigation nobody watched take effect — each
is indistinguishable from the working version until the night you need it.

**Proof of an undo expires, and a date by itself has no failure mode.** An
untested rollback is byte-for-byte identical to a working one until the night it
is needed, and a restore proved a year ago against a since-migrated schema reads
in the record exactly like one proved on Tuesday. So every undo, restore,
runbook and escalation path carries a state — `proved` · `simulated` · `stale` ·
`untested` · `unprovable` — and two clocks, whichever fires first: an interval
with a stated reason, and a **named surface** whose change voids the proof
immediately. Naming the surface is what gives the date something to fail against.

**Only execution upgrades a state.** A dry run reaches `simulated`, never
`proved`; re-reading the runbook moves nothing
([`_operation/EXPIRY.md`](skills/_operation/EXPIRY.md)).

## How it is put together

A skill is loaded in three stages. The **listing** carries `name` and
`description` only, on every turn. **`SKILL.md`** is read in full once a skill
is chosen. Anything it points at is read only when the situation calls for it.

**Selection happens on the description alone**, so every word that selects a
skill appears literally in its description, and
[`operation-registry/capabilities.yaml`](operation-registry/capabilities.yaml)
lists those words per skill. A rule checks the two agree.

**Boundaries live in one file** — that same registry's `not:`. Descriptions
never name a neighbour. If they did, adding a sixth skill would mean editing the
other five.

**Contracts are delivered, not referenced.** The operative part of each contract
is copied verbatim into every `SKILL.md`; `make render` writes it back and a rule
fails on drift.

**Knowledge splits by whether it rots.** `playbooks/` holds judgement and is
budgeted. `reference/` holds what goes stale — deploy strategies, severity
matrices, maturity models — carries no line budget, and states its purpose and a
checked-on date instead.

**A grade that names a source can be checked against that source.** The two
pages below state how `ansible`, `aws` and `gcloud` behave. The Ansible claims
are graded `O1` — measured — so `make figures` **re-runs them** against a local
inventory. The AWS and Google Cloud claims are graded `O3` — the tool's own
documentation — so it re-reads that documentation on the installed CLIs: every
cited command still resolves, every quoted sentence is still there, and the
pages are still quoting it. It runs in `make check` and the pre-commit hook, and
eight deliberate breaks were each observed failing it. A missing CLI reports
SKIPPED for that tool and passes; that hole is announced rather than hidden,
because a check that silently passes when it cannot run is worse than no check.

**The contract asks for `O1`, so the set says how to get it.** `O1` is *command
output captured now*, and for a long time nothing here named a command. Two
pages close that, both strictly read-only — the set still does not operate the
system, it observes it.
[`capture-commands`](skills/operation-incident/reference/capture-commands.md)
is what to run in the 60 seconds before a mitigation, ordered by what each one
destroys: re-running a playbook converges, and convergence erases the divergence
you were trying to explain, while an autoscaler destroys the same evidence on a
clock nobody started.
[`observation-traps`](skills/operation-incident/reference/observation-traps.md)
is the commands that succeed while answering a different question. Measured:
a play whose shell task runs `true` reports `changed=2`, and check mode *skips*
that task rather than simulating it — so neither number says what it looks like
it says. Quoted: `--dry-run` returns `DryRunOperation` **as an error** when it
succeeds, `--no-paginate` returns "only … the first page of results" with
nothing marking the boundary, and an omitted `--project` means "the current
project is assumed" — ambient shell state deciding which environment a responder
is describing.

**Budgets are enforced, not intended.**
[`operation-registry/harness.yaml`](operation-registry/harness.yaml) holds every
threshold; `operation-tools/validate.py` decides them and CI fails on a violation.

## Names, and why none of them are generic

A skills directory is flat and shared with every other set on the machine, so a
generic name placed there is a silent collision. This set's shared directory used
to be `_shared`, which a sibling set also used, and `_common` in that same
directory belongs to a third.

**One declaration.** `set: operation` in the harness file is the only place the
name is written; the prefix, the shared directory (`_operation/`), and the label
every document carries all derive from it.

**Every directory this set owns carries the set name**, with `skills/` exempt as
the place `install.sh` looks. Carrying the prefix is not what makes something
installable — a skill is a directory holding a `SKILL.md`, and only those are
linked.

**Everything a skill reads lives inside the skill**, reached through symlinks
named `_operation` and `registry`. Relative paths are normalised *lexically*, so
`../_operation/X.md` would not travel back through the install symlink — a shell
follows the link and finds the file, which is what makes that fail quietly.

## Files

| File | What it fixes |
|---|---|
| [`skills/_operation/CONTRACT.md`](skills/_operation/CONTRACT.md) | The rungs, reporting shape, status, residuals, the sweep |
| [`skills/_operation/SAFETY_TIERS.md`](skills/_operation/SAFETY_TIERS.md) | What an action can destroy, and what that demands |
| [`skills/_operation/SIZING.md`](skills/_operation/SIZING.md) | The two scales, when a dialogue is mandatory, and what pressure may not change |
| [`skills/_operation/VALUES.md`](skills/_operation/VALUES.md) | The order when two goods conflict, and the escape hatch |
| [`skills/_operation/HANDOFF.md`](skills/_operation/HANDOFF.md) | What passes between skills |
| [`skills/_operation/ROUTING.md`](skills/_operation/ROUTING.md) | Guidance. Which skill owns the question |
| [`skills/_operation/GLOSSARY.md`](skills/_operation/GLOSSARY.md) | Shared terms, and the output language rule |

## Layout

```
operations-skills/
├── README.md
├── Makefile
├── install.sh
├── operation-registry/           # budgets, boundaries, routes, delivered blocks
├── operation-tools/              # validate · test_validate · render · pre-commit
└── skills/                       # where install.sh looks
    ├── _operation/               # contracts in force on every run
    └── operation-<facet>/
        ├── SKILL.md              # Owns / Before starting / Decide first /
        │                         # Always·Never / Verify with / Done when
        ├── _operation -> ../_operation
        ├── registry   -> ../../operation-registry
        ├── playbooks/            # judgement. Budgeted, and must not rot
        └── reference/            # what goes stale. No line budget, dated instead
```

Artifacts these skills produce — postmortems, change records, runbooks, PRRs,
rotations — live in the host organisation's tree under `.operations/`, declared
as external so the path checker does not read them as references into this repo.

## Working on it

```sh
make check      # what CI runs: the rules, then proof the rules still fire
make render     # after editing anything in operation-registry/delivered/
make hooks      # run the rules on every commit
```

## Installing

```sh
./install.sh                    # symlink skills/operation-* into ~/.claude/skills
make link                       # the same thing, via make
```

Each `operation-*` skill is linked individually and reaches its contracts through
the symlinks inside it. Nothing un-prefixed is copied anywhere.

## What this does not guarantee

- **`allowed-tools` is one CLI's mechanism.** Where a tool grant is not
  enforced, the `Never` lines are discipline and nothing more. Four of five
  skills hold `Bash`, so a determined misuse is always reachable
- **Nothing here stops a skill acting on production.** The class says what it may
  write locally; whether a command observes or changes is read by a person
- **The fixtures do not model how a model chooses.** They catch a missing or
  duplicated signal, not a misroute
- **`Verified:` dates are not checked against anything.** A stale reference file
  with a fresh date passes
- **No rule checks that a rung was honestly assigned.** The contract says every
  claim carries one; whether `O1` was earned is read by a person — and this is
  the domain where that gap costs most

## The published overview

[`docs/index.html`](docs/index.html) is a generated page — every figure on it is
read off this repository, the way `make figures` recomputes what the reference
layer states. **Do not edit it by hand**: `tools/pages.py` in the `agent-toolkit`
repository writes it, `tools/pages.py --check` fails when it is behind, and
`.github/workflows/pages.yml` here only publishes what is committed.

