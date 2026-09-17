<!-- operation:deferred -->
# Capture Commands — Producing `O1` Before It Is Gone

Purpose: Scoped observation commands and unsafe lookalikes for producing `O1` evidence on the platforms this set is used against, ordered by how fast the evidence disappears, and what each mitigation destroys as it runs.
Read when: an incident is live and a playbook re-run, an instance replacement, a service redeploy, or a rollout is about to happen — or has just happened and the evidence is being reconstructed.
Source: Ansible check-mode and setup documentation; AWS CLI and Google Cloud SDK help (links and quotations below).
Verified: 2026-08-21 — the Ansible behaviour below was produced by running it against a local inventory (`O1`). The `aws` and `gcloud` behaviour is quoted from `aws help` / `gcloud help` on the installed CLIs (`O3`); no credentials were available in this session, so nothing on those two was executed.
Claims not from either source — ingestion lag, retention windows, what a given account has configured — are `O5` and are worth confirming against the environment actually in use.
`make figures` re-checks every quoted claim against the CLIs on PATH, in `make check` and the pre-commit hook. With a CLI missing it reports SKIPPED for that tool and passes: a hole, announced rather than hidden.

`_operation/CONTRACT.md` puts **command output captured now** at the top of the
evidence ladder, and `impact-assessment.md` gives the capture 60 seconds. This
page is what to run in them.

Only verified read-only observations may be executed by the agent. A familiar tool name
or a dry-run flag does not establish that property; unreviewed commands stay proposals.
Before capture, bind the expected environment/account/project/region and resource to the
incident; record the effective identity, command, UTC capture time and covered window.
Verify returned identity and resource against that expectation. Command success alone is not O1
for the intended target. Check pagination, truncation, ingestion lag and output redaction;
record a bounded sample as a sample, not fleet-wide absence. Do not run extra commands merely
to earn O1. Preserve only evidence relevant to the claim, before convergence/autoscaling erases it.

---

## What each mitigation takes with it

This is the part that decides the order. Mitigation is still first — but knowing
what a given action erases turns "capture everything" into three commands.

| Mitigation | Destroyed the moment it runs | Grab first |
|---|---|---|
| Re-run the playbook | The diverged state itself. Convergence is the point of Ansible and it is also what erases the difference you were trying to explain | Read-only state/log capture; check mode and facts require the review below |
| Terminate or replace an instance | Instance store, memory, anything not on a persistent disk | Console/serial output; a new disk snapshot is a proposed human mutation, not a read |
| Redeploy a service | The failing tasks and the reason each one stopped | The stopped tasks' own records, before they age out |
| Roll a managed instance group | Every VM in the group, in sequence, on a schedule you started | Anything from one unhealthy member |
| **An autoscaler or health check acting on its own** | The same, **on a clock you do not control** | Everything, immediately — this is the only row where waiting is itself the loss |
| Time passing | Log ingestion windows, and any short-retention metric | The log export, scoped to the incident window |

## Ansible — before you converge

```sh
ansible <pattern> -i <reviewed-static-inventory> --list-hosts
```

Use only reviewed inventory and plugins: dynamic inventory can execute controller-side code.
The host list is selection evidence, not proof of the remote environment's identity.
**`ansible-playbook --check --diff` is ambiguous, not an observation shortcut.**
Ansible permits `check_mode: false` tasks to make changes even under `--check`.
`setup` can execute custom facts from `fact_path`; `--tree` also writes local files.
Do not run an unreviewed playbook or fact collector to obtain O1. Inspect tasks, modules,
plugins, delegation and custom facts first; use an established passive query instead.
See the [check-mode contract](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html)
and [setup parameters](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/setup_module.html).
These are documented safety properties (O3); local negative tests do not prove production safety.

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
aws sts get-caller-identity --profile <profile> --region <region> --output json
aws ec2 describe-instances --instance-ids <id> --profile <profile> --region <region> --output json
aws ec2 get-console-output --instance-id <id> --profile <profile> --region <region> --output json
aws ecs describe-tasks --cluster <cluster-arn> --tasks <task-arn> --profile <profile> --region <region> --output json
aws logs tail <group> --since 15m --profile <profile> --region <region>
```

Run `get-caller-identity` first and put its output in the timeline. Every other
command on this page is meaningless if it ran against the wrong account, and
the resource output alone does not establish the caller. Keep the same explicit profile and region;
compare the STS identity with the expected account, not just a successful exit. Logs tail is a
relative-window text sample; record capture time and returned event timestamps, not a full-history claim.

## Google Cloud — before you roll

```sh
gcloud config list --format=json
gcloud auth list --format=json
gcloud compute instances describe <vm> --zone <z> --project <project> --account <account> --format=json
gcloud compute instances get-serial-port-output <vm> --zone <z> --project <project> --account <account> --format=json
gcloud logging read 'resource.type="gce_instance" AND resource.labels.instance_id="<id>" AND timestamp>="<start-UTC>" AND timestamp<="<end-UTC>"' --limit 200 --project <project> --account <account> --format=json
```

`gcloud help` states that `--project`, when omitted, means "the current project
is assumed". The current project is ambient shell state, so two responders
running the identical command can be describing two different environments and
comparing notes as though they were not. Pass `--project` explicitly during an
incident, and record it. Resolve any configured impersonation before using these templates:
`gcloud auth list` alone does not establish the effective principal. Stop if it is unverified.
The 200-record limit is a cap, not evidence of complete coverage; narrow the window or continue
capture when completeness matters. Serial output can be partial; record offsets and gaps.

## Exporting rather than reading

Terminal scrollback is not evidence. Redirect to a file, name it for the
incident, and say in the timeline where it went. Redirection mutates a local artifact,
not production; use an approved destination and do not overwrite an earlier capture.

```sh
aws ec2 describe-instances --instance-ids <id> --profile <profile> --region <region> --output json > inc-<id>-instance.json
gcloud compute instances describe <vm> --zone <z> --project <project> --account <account> --format=json > inc-<id>-vm.json
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
