<!-- operation:deferred -->
# Capture Commands — Producing `O1` Before It Is Gone

Purpose: The read-only commands that produce `O1` evidence on the platforms this set is used against, ordered by how fast the evidence disappears, and what each mitigation destroys as it runs.
Read when: an incident is live and a playbook re-run, an instance replacement, a service redeploy, or a rollout is about to happen — or has just happened and the evidence is being reconstructed.
Source: none — nothing outside this page can move what it states.
Verified: 2026-08-21 — the Ansible behaviour below was produced by running it against a local inventory (`O1`). The `aws` and `gcloud` behaviour is quoted from `aws help` / `gcloud help` on the installed CLIs (`O3`); no credentials were available in this session, so nothing on those two was executed.
Claims not from either source — ingestion lag, retention windows, what a given account has configured — are `O5` and are worth confirming against the environment actually in use.
`make figures` re-checks every quoted claim against the CLIs on PATH, in `make check` and the pre-commit hook. With a CLI missing it reports SKIPPED for that tool and passes: a hole, announced rather than hidden.

`_operation/CONTRACT.md` puts **command output captured now** at the top of the
evidence ladder, and `impact-assessment.md` gives the capture 60 seconds. This
page is what to run in them.

Everything here is read-only. None of it operates the system; it is what makes
the difference between a postmortem with a cause and one with a theory.

---

## What each mitigation takes with it

This is the part that decides the order. Mitigation is still first — but knowing
what a given action erases turns "capture everything" into three commands.

| Mitigation | Destroyed the moment it runs | Grab first |
|---|---|---|
| Re-run the playbook | The diverged state itself. Convergence is the point of Ansible and it is also what erases the difference you were trying to explain | `--check --diff`, and the facts |
| Terminate or replace an instance | Instance store, memory, anything not on a persistent disk | Console/serial output, a disk snapshot |
| Redeploy a service | The failing tasks and the reason each one stopped | The stopped tasks' own records, before they age out |
| Roll a managed instance group | Every VM in the group, in sequence, on a schedule you started | Anything from one unhealthy member |
| **An autoscaler or health check acting on its own** | The same, **on a clock you do not control** | Everything, immediately — this is the only row where waiting is itself the loss |
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
aws sts get-caller-identity              # which account and identity this is
aws ec2 describe-instances --instance-ids <id>
aws ec2 get-console-output --instance-id <id>     # survives the instance, briefly
aws ecs describe-tasks --cluster <c> --tasks <arn> # stoppedReason, before it ages out
aws logs tail <group> --since 15m                 # scoped, not the whole group
```

Run `get-caller-identity` first and put its output in the timeline. Every other
command on this page is meaningless if it ran against the wrong account, and
nothing in their output says which account that was.

## Google Cloud — before you roll

```sh
gcloud config list                       # the project this shell is pointed at
gcloud auth list                         # which account is active
gcloud compute instances describe <vm> --zone <z>
gcloud compute instances get-serial-port-output <vm> --zone <z>
gcloud logging read 'resource.type="gce_instance"' --limit 200 --freshness 1h
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
aws ec2 describe-instances --instance-ids <id> > inc-<id>-instance.json
gcloud compute instances describe <vm> --zone <z> --format=json > inc-<id>-vm.json
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
