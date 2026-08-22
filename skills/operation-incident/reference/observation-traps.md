<!-- operation:deferred -->
# Observation Traps — Commands That Succeed and Answer Something Else

Purpose: Read-only commands whose output is routinely read as evidence for a claim it does not support, and the command that does support it.
Read when: citing any command output as `O1`, verifying that a mitigation worked, or explaining why two responders disagree while quoting the same command.
Verified: 2026-08-21 — the Ansible behaviour was produced by running it against a local inventory (`O1`). The `aws` and `gcloud` behaviour is quoted from `aws help` / `gcloud help` on the installed CLIs (`O3`); no credentials were available, so nothing on those two was executed.
Claims from neither source are `O5` and are worth confirming against the environment in use.
`make figures` re-checks every quoted claim against the CLIs on PATH, in `make check` and the pre-commit hook, and reports SKIPPED per missing tool rather than passing quietly.

None of these commands fails. Each returns a clean, plausible answer to a
question slightly different from the one being asked, which is why the mistake
survives review — there is no error to notice, only a value that means something
else.

---

## `changed=` is a claim, not an observation

Ansible's recap counts what each module *reported*. A module decides its own
`changed` value, and `shell` and `command` have no way to know, so they report
changed every time unless a `changed_when` says otherwise.

Measured on a two-task play whose shell task ran `true`:

```
localhost : ok=2  changed=2  unreachable=0  failed=0
```

Nothing changed. So `changed=0` does not mean the run was a no-op, and a
non-zero `changed` does not mean anything was modified. What it means is
`declarative tasks that reported a difference + every shell task you ran`.

The evidence for whether the system changed is `--diff` on the declarative
tasks, or a read of the thing itself afterwards.

## `--check` is not a dry run

Same play, in check mode:

```
localhost : ok=1  changed=1  unreachable=0  failed=0  skipped=1
```

The shell task was **skipped**, not simulated. Anything downstream that depended
on its result then evaluated against state that never existed. A clean check run
is evidence about the declarative tasks and about nothing else — and the tasks
it could not check are the ones most likely to be doing the dangerous thing.

Pair it with `--diff`, and say in the report which tasks check mode skipped.

## `--list-hosts` has to be read, not exit-checked

Measured: `ansible nosuchhost -i inv --list-hosts` exits **0**. It prints a
warning and a zero.

The playbook itself is stricter — `ansible-playbook --limit nosuchhost` exits
**1** with "leaves us with no hosts to target" — so a mistyped limit fails
loudly there. But the pre-flight that is supposed to catch it beforehand does
not fail. Read the host list; do not wrap it in `&&`.

## `--dry-run` reports success as an error

`aws ec2 describe-instances help` states it plainly:

> Checks whether you have the required permissions for the operation, without
> actually making the request, and provides an error response. **If you have the
> required permissions, the error response is `DryRunOperation`.** Otherwise, it
> is `UnauthorizedOperation`.

So the success case is a non-zero exit with an error in it. Any wrapper that
treats exit status as the answer reads a working dry run as a failure, and — the
expensive direction — reads `UnauthorizedOperation` as "the check ran". Match on
the error code, never on the exit status.

## `--query` filters what already arrived

`aws help`: `--query` is "a JMESPath query to use in filtering **the response
data**". It runs client-side, on what came back. It cannot make the API return
anything it did not, and it cannot distinguish "no matches" from "the field is
spelled differently in this API version".

An empty result from a `--query` is a statement about the query at least as
often as about the fleet. Before reporting an absence, drop the query and look
at one raw record.

## `--no-paginate` truncates silently

`aws help`: with automatic pagination disabled "the AWS CLI will only make one
call, for the first page of results". There is no marker in the output saying a
page boundary was reached. `--max-items` behaves the same way.

During an incident this is how a fleet-wide problem gets reported as affecting
the first N instances.

## The account and the project are ambient

Neither CLI puts the identity it used into ordinary output.

- `gcloud help` on `--project`: omitted, "the current project is assumed" — and
  the current project is shell state that differs between two responders.
- `gcloud help` on `--impersonate-service-account`: "all API requests will be
  made as the given service account … instead of the currently selected
  account". After that, `gcloud auth list` is not the identity that acted.

So the first line of any capture is `aws sts get-caller-identity` or
`gcloud config list` plus `gcloud auth list`, recorded in the timeline. Pass
`--profile` / `--region` / `--project` explicitly for the rest of the incident:
a command that means something different in someone else's shell is not
reproducible evidence.

## `--quiet` answers the confirmation for you

`gcloud help` on `--quiet`: "Disable all interactive prompts … **If input is
required, defaults will be used**, or an error will be raised."

The prompt exists because the operation is not obviously safe. `--quiet` does
not skip the decision; it takes the default one, unattended, and the output
looks like a command that simply worked.

## Human-friendly output is not the record

`gcloud help` on `--format`: the default is "a command-specific human-friendly
output format" — columns chosen to fit a terminal. What was dropped is not
marked. Ask for `--format=json`, or `--output json` on AWS, for anything that
goes into a timeline or a postmortem.

## Verifying a mitigation worked

The failure mode here is the same as the rest of the page — checking the signal
that is easiest to reach rather than the one that carries user impact.

- **Not** "the playbook run was green" — it converged, which erases the symptom
  and the evidence together
- **Not** "the instances are healthy" — they were healthy during the outage
- **Not** "the error rate on the dashboard dropped" alone, if traffic dropped too
- **Yes** the user-facing indicator named in the impact statement, back inside
  its threshold, measured over a window long enough to exclude the dip that any
  replacement produces

Until that indicator is back, impact has not ended, whatever the infrastructure
view says. State the window and the value: `checkout success 99.4% over 10 min
[O1: <dashboard>, 14:32 JST]` beats "recovered".
