<!-- operation:deferred -->
# Capture Commands — Producing `O1` Before It Is Gone

Purpose: The read-only commands that produce `O1` evidence on the platforms this set is used against, ordered by how fast the evidence disappears, and what each mitigation destroys as it runs.
Read when: an incident is live and a playbook re-run, an instance replacement, a service redeploy, or a rollout is about to happen — or has just happened and the evidence is being reconstructed.
Source: none pinned — the installed `ansible`, `aws` and `gcloud` CLIs, unversioned; `make figures` re-reads them.
Verified: 2026-08-21 — the Ansible behaviour below was produced by running it against a local inventory (`O1`). The `aws` and `gcloud` behaviour is quoted from `aws help` / `gcloud help` on the installed CLIs (`O3`); no credentials were available in this session, so nothing on those two was executed.
Claims not from either source — ingestion lag, retention windows, what a given account has configured — are `O5` and are worth confirming against the environment actually in use.
`make figures` re-checks every quoted claim against the CLIs on PATH, in `make check` and the pre-commit hook. With a CLI missing it reports SKIPPED for that tool and passes: a hole, announced rather than hidden.

`_operation/CONTRACT.md` puts **command output captured now** at the top of the
evidence ladder, and `reference/impact-assessment.md` gives the capture 60 seconds. This
page is what to run in them.

Of the Ansible forms below, `--list-hosts` only reads the inventory. `--check` still runs
`check_mode: false` tasks (grep the play, its roles and imports), and both `--check` and
`-m setup` run `facts.d` scripts on the host (`--check` unless `gather_facts: false`). Until
cleared each of those two is a person's `T2`; the agent runs only cleared reads. `--diff` prints secrets unless `no_log`, and logs that may
hold personal data are sensitive reads: `T3` (`_operation/SAFETY_TIERS.md` rule 4).

---

## What each mitigation takes with it

This is the part that decides the order. Mitigation is still first — but knowing
what a given action erases turns "capture everything" into three commands.

| Mitigation | Destroyed the moment it runs | Grab first |
|---|---|---|
| Re-run the playbook | The diverged state itself. Convergence is the point of Ansible and it is also what erases the difference you were trying to explain | `--check --diff`, and the facts |
| Terminate or replace an instance | Instance store, memory, anything not on a persistent disk | Console/serial output. A disk snapshot is a create, not a read: a person's `T2` |
| Redeploy a service | The failing tasks and the reason each one stopped | The stopped tasks' own records, before they age out |
| Roll a managed instance group | Every VM in the group, in sequence, on a schedule you started | Anything from one unhealthy member |
| **An autoscaler or health check acting on its own** | The same, **on a clock you do not control** | Every read, immediately; pausing the autoscaler or snapshotting is a person's `T2` — ask now. The only row where waiting is itself the loss |
| Time passing | Log ingestion windows, and any short-retention metric | The log export, scoped to the incident window |

## Ansible — before you converge

```sh
ansible <pattern> -i <inventory> --list-hosts        # what the pattern actually matches
ansible-playbook -i <inv> <play.yml> --check --diff  # what would change, per file
ansible <pattern> -i <inv> -m setup                  # the facts, as they are now
```

**`--list-hosts` is a read, not an exit code.** Measured: a pattern matching
nothing returns exit status 0 from `ansible --list-hosts`. Only the playbook
itself fails on an empty target — `ansible-playbook --limit nosuchhost` exits 1
with "leaves us with no hosts to target". Reading the host list is the check;
running it and getting a zero is not.

**`--check` does not tell you what a `shell` or `command` task would do.**
Measured on a two-task play: check mode reported `ok=1 changed=1 skipped=1` —
the shell task was skipped, not simulated. Every task downstream of it then runs
against state that never happened. Treat a check-mode run as evidence about the
declarative tasks and about nothing else.

## AWS — before you replace

```sh
aws sts get-caller-identity --profile <p>             # which account and identity this is
aws ec2 describe-instances --instance-ids <id> --profile <p> --region <r>
aws ec2 get-console-output --instance-id <id> --profile <p> --region <r>
aws ecs describe-tasks --cluster <c> --tasks <arn> --profile <p> --region <r>  # stoppedReason, before it ages out
aws logs filter-log-events --log-group-name <g> --start-time <ms> --end-time <ms> \
  --profile <p> --region <r>                              # the incident window, not "recent"
```

Run `get-caller-identity` first, record it, and compare its `Account` with the account
that owns the target. On a mismatch nothing after it is `O1` for this incident — and
nothing in the other commands' output says which account they ran against.

## Google Cloud — before you roll

```sh
gcloud config list                       # the project this shell is pointed at
gcloud config get-value auth/impersonate_service_account  # when set, this acts, not auth list
gcloud compute instances describe <vm> --zone <z> --project <p>
gcloud compute instances get-serial-port-output <vm> --zone <z> --project <p>
gcloud logging read 'resource.type="gce_instance" AND resource.labels.instance_id="<id>"
  AND timestamp>="<start>" AND timestamp<="<end>"' --project <p> --format=json
```

`gcloud help` states that `--project`, when omitted, means "the current project
is assumed". The current project is ambient shell state, so two responders
running the identical command can be describing two different environments and
comparing notes as though they were not. Pass `--project` explicitly during an
incident, and record it.

## Exporting rather than reading

Terminal scrollback is not evidence. Redirect to a file, name it for the
incident, and say in the timeline where it went.

```sh
aws ec2 describe-instances --profile <p> --region <r> --instance-ids <id> > inc-<id>-instance.json
gcloud compute instances describe <vm> --project <p> --zone <z> --format=json > inc-<id>-vm.json
ansible <pattern> -i <inv> -m setup --tree ./inc-<id>-facts/
```

Ask for JSON explicitly. `gcloud help` says the default format is
"a command-specific human-friendly output format" — human-friendly means
columns chosen for a terminal, and what got dropped is not marked.

## When nothing was captured

Say so as a finding, at the rung it deserves. "No `O1` for the 13:40–13:55
window; the autoscaler had already replaced both instances before capture
started" is a complete, honest statement. A postmortem that quietly
reconstructs that window from reasoning is `O5` wearing `O1`'s label, and every
conclusion drawn from it inherits the grade.
