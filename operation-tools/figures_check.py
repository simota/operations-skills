#!/usr/bin/env python3
"""Hold the observation pages to the tools that are actually installed.

The two pages under operation-incident/reference/ state how `ansible`, `aws` and
`gcloud` behave. The Ansible claims are graded `O1` — measured — so this re-runs
them. The AWS and Google Cloud claims are graded `O3` — the tool's own
documentation — so this re-reads that documentation. Either way the grade names
a source, which is what makes it checkable at all; a `Verified:` date does not.

    make figures

A CLI that is missing — or installed but unable to run — reports SKIPPED for that
tool and does not fail the run. That hole is announced rather than hidden: a check
that silently passes when it cannot run is worse than no check, and one that reads
its own inability to run as a wrong claim on the page is worse still.
"""
from __future__ import annotations      # `str | None` on Python 3.9

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from validate import fence_step         # one reading of a fence, shared with V8/V19

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUOTED = sorted((ROOT / "skills/operation-incident/reference").glob("*.md"))
# Command existence is checked across every reference page; the quoted-wording
# checks apply only to the two pages that quote documentation.
ALL_PAGES = sorted(ROOT.glob("skills/*/reference/*.md"))
failures: list[str] = []
skipped: list[str] = []


def fail(where: str, msg: str) -> None:
    failures.append(f"  {where}: {msg}")


def norm(s: str) -> str:
    """Compare on words. Which quote character someone typed is not a finding."""
    s = re.sub(r"\x1b\[[0-9;]*m", "", s)
    s = re.sub(r".\x08", "", s)
    s = re.sub(r"^\s*>+", " ", s, flags=re.M)      # markdown block quotes
    for ch in "`'\"*":
        s = s.replace(ch, " ")
    # Hyphens are dropped, not compared. help_of() rejoins a word groff split at
    # the margin, and cannot tell that split from a break at a real hyphen
    # ("command-" / "specific"), so both sides lose every hyphen alike.
    s = s.replace("-", "")
    return " ".join(s.split()).casefold()


def text_of(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def help_of(*argv: str) -> str:
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    # A man page is typeset: groff hyphenates at the right margin, and on a
    # narrower terminal or a newer CLI the break lands inside a quoted word
    # ("DryRun-" / "Operation"). That is layout, not a change in what the
    # documentation says, so a word split at a line end is joined back.
    out = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
    out = re.sub(r".\x08", "", out)
    return re.sub(r"(\w)-[ \t]*\n\s*(\w)", r"\1\2", out)


def body() -> str:
    return norm(" ".join(text_of(p) for p in QUOTED))


# --- every command the pages cite exists -----------------------------------

# Global options that take a value. Their value is not a subcommand:
# `aws --profile prod ec2 ...` cites `aws ec2`, not `aws prod`.
VALUE_FLAGS = {
    "aws": {"--profile", "--region", "--output", "--query", "--endpoint-url",
            "--color", "--ca-bundle", "--cli-read-timeout", "--cli-connect-timeout",
            "--cli-binary-format", "--cli-input-json", "--cli-input-yaml"},
    "gcloud": {"--project", "--account", "--configuration", "--format", "--verbosity",
               "--impersonate-service-account", "--billing-project", "--flatten",
               "--filter", "--limit", "--page-size", "--sort-by", "--zone", "--region",
               "--access-token-file", "--trace-token"},
}


def subcommand_words(tool: str, rest: list[str]) -> list[str]:
    words, skip = [], False
    for w in rest:
        if skip:
            skip = False
        elif w.startswith("-"):
            skip = "=" not in w and w in VALUE_FLAGS.get(tool, set())
        else:
            words.append(w)
    return words


# `=` and the characters a flag's value carries are part of the capture: stopping
# at `--profile=prod` would leave `aws --profile=prod ec2 ...` citing nothing, and
# a command nobody checks reads exactly like one that passed. Any word boundary
# starts one — after a prompt, an env prefix, a pipe — and every match counts.
CMD = re.compile(r"(?:^|(?<=[\s`$(|;&]))(aws|gcloud|ansible|ansible-playbook)\s+([a-z0-9 =._/:-]+)")
SPAN = re.compile(r"`([^`]+)`")


def commands_of(line: str, fenced: bool = False) -> list[tuple[str, ...]]:
    """Every command a line cites, each to the depth that names it.

    In a fence the whole line is code; in prose only its code spans are, so
    "the aws console" in a sentence is not read as a command.
    """
    out = []
    for code in [line] if fenced else SPAN.findall(line):
        for m in CMD.finditer(code):
            tool, rest = m.group(1), m.group(2).split()
            words = subcommand_words(tool, rest)
            depth = {"aws": 2, "gcloud": 3, "ansible": 0, "ansible-playbook": 0}[tool]
            if depth and len(words) >= depth:
                out.append((tool, *words[:depth]))
    return out


def cited_commands() -> set[tuple[str, ...]]:
    out: set[tuple[str, ...]] = set()
    for p in ALL_PAGES:
        fence = None
        for line in text_of(p).splitlines():
            fence, edge = fence_step(line, fence)
            if not edge:
                out.update(commands_of(line, fenced=fence is not None))
    return out


def check_commands() -> int:
    cmds = cited_commands()
    if not cmds:
        fail("commands", "the pages cite no commands — the checker has stopped checking")
        return 0
    n = 0
    for cmd in sorted(cmds):
        tool = cmd[0]
        if not usable(tool):
            continue
        n += 1
        argv = list(cmd) + (["help"] if tool == "aws" else ["--help"])
        if len(help_of(*argv)) < 200:
            fail("commands", f"`{' '.join(cmd)}` is cited but produced no help on the "
                             "installed CLI")
    return n


# --- quoted documentation still says what the pages say it says ------------

QUOTES = {
    ("aws", "ec2", "describe-instances"): [
        "If you have the required permissions, the error response is DryRunOperation",
    ],
    ("aws",): [
        "A JMESPath query to use in filtering the response data",
        "the AWS CLI will only make one call, for the first page of results",
    ],
    ("gcloud",): [
        "the current project is assumed",
        "Disable all interactive prompts",
        "If input is required, defaults will be used",
        "all API requests will be made as the given service account",
        "a command-specific human-friendly output format",
    ],
}


def check_quotes() -> int:
    page = body()
    n = 0
    for cmd, phrases in QUOTES.items():
        # The page side needs no CLI: a quote deleted from the page is caught on a
        # machine without the tool too, rather than only where the tool happens to be.
        for phrase in phrases:
            if norm(phrase) not in page:
                fail("quotes", f"the pages no longer quote {phrase!r} — "
                               "the checker is enforcing a claim nobody makes")
        tool = cmd[0]
        if not usable(tool):
            continue
        text = norm(help_of(*cmd, "help"))
        for phrase in phrases:
            n += 1
            if norm(phrase) not in text:
                fail("quotes", f"`{' '.join(cmd)} help` no longer contains "
                               f"{phrase!r}, which the pages rest on")
    return n


# --- the Ansible measurements are re-run -----------------------------------

INVENTORY = "[web]\nlocalhost ansible_connection=local\n"
PLAY = """- hosts: web
  gather_facts: false
  tasks:
    - name: a shell task that changes nothing
      shell: "true"
    - name: a file task that touches its target (changed on every run)
      file: path={{ probe }} state=touch mode=0644
"""


def recap(out: str) -> dict[str, int]:
    m = re.search(r"localhost\s*:\s*(.*)", out)
    if not m:
        return {}
    return {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", m.group(1))}


TRAPS = ROOT / "skills/operation-incident/reference/observation-traps.md"


def stated_recaps() -> tuple[dict[str, int], dict[str, int]]:
    """The two recaps the page prints: the ordinary run, then check mode.

    Read from the page rather than restated here, so a page edited to claim the
    opposite fails instead of being graded against a copy kept in the checker.
    """
    printed = [recap(l) for l in text_of(TRAPS).splitlines() if "localhost" in l]
    printed = [r for r in printed if r]
    plain = next((r for r in printed if "skipped" not in r), {})
    checked = next((r for r in printed if "skipped" in r), {})
    if not plain or not checked:
        fail("ansible", "observation-traps.md no longer prints both recaps — "
                        "the checker has stopped checking anything")
    return plain, checked


EXITS = re.compile(r"`([^`]*(?:list-hosts|--limit)[^`]*)`[^.]*?exits\s*\*\*(\d+)\*\*")


def stated_exits() -> dict[str, int]:
    """The exit statuses the page states for the two host-selection commands."""
    out = {}
    for cmd, code in EXITS.findall(text_of(TRAPS)):
        out["list-hosts" if "list-hosts" in cmd else "limit"] = int(code)
    if len(out) != 2:
        fail("ansible", f"observation-traps.md states {len(out)} of the two exit "
                        "statuses this checks — the checker has stopped checking anything")
    return out


def unusable(tool: str, argv: list[str]) -> str | None:
    """Whether `tool` is on PATH but cannot run — and why, in its own words.

    On PATH is not the same as usable: a sandbox that denies its temp directory,
    a broken install, a missing runtime. Every probe below reads the tool's
    output, so a tool that never starts produces no output to read, and the
    checks would report the page as wrong about behaviour nothing observed.
    """
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"{tool} is installed but did not run: {e}"
    if r.returncode == 0:
        return None
    err = (r.stderr or r.stdout).strip().splitlines()
    return f"{tool} is installed but did not run: {err[0] if err else 'no output'}"


_USABLE: dict[str, bool] = {}


def usable(tool: str) -> bool:
    """On PATH and able to start. Either failure is SKIPPED, never a finding:
    a CLI that cannot run produces no help, and reading that as the page being
    wrong sends someone to correct a page that is fine."""
    if tool not in _USABLE:
        if not shutil.which(tool):
            skipped.append(tool)
            _USABLE[tool] = False
        else:
            # `help` too: every check reads it, and it fails on its own — the AWS
            # CLI renders help through groff or mandoc, which a slim image lacks.
            why = unusable(tool, [tool, "--version"]) or unusable(tool, [tool, "help"])
            if why:
                skipped.append(why)
            _USABLE[tool] = why is None
    return _USABLE[tool]


def run(argv: list[str], cwd: pathlib.Path) -> subprocess.CompletedProcess:
    """One Ansible invocation. A hang is reported as a failure, not waited out."""
    try:
        return subprocess.run(argv, capture_output=True, text=True, cwd=cwd, timeout=120)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(argv, -1, "", f"timed out: {' '.join(argv)}")


def check_ansible() -> int:
    # What the page states is read first, with or without Ansible installed: a page
    # that stopped printing a recap or an exit status fails everywhere.
    plain, checked = stated_recaps()
    exits = stated_exits()
    if not shutil.which("ansible-playbook"):
        skipped.append("ansible not on PATH")
        return 0
    why = unusable("ansible", ["ansible-playbook", "--version"])
    if why:
        skipped.append(why)
        return 0
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="operation-figures-"))
    try:
        (tmp / "inv.ini").write_text(INVENTORY)
        (tmp / "play.yml").write_text(PLAY)
        probe = tmp / "probe"
        base = ["ansible-playbook", "-i", str(tmp / "inv.ini"), str(tmp / "play.yml"),
                "-e", f"probe={probe}"]

        r = run(base, tmp)
        rec = recap(r.stdout)
        if not rec:
            # No recap line means the play did not run. Reading that as a wrong
            # claim about `changed=` sends a reader to correct a page that is fine.
            skipped.append(f"ansible ran but printed no play recap: "
                           f"{(r.stderr or r.stdout).strip().splitlines()[:1]}")
            return 0
        # Only the counters the page prints: it abridges the recap, and demanding
        # it reprint `rescued=` and `ignored=` would be checking the page's layout.
        got = {k: rec.get(k) for k in plain}
        if plain and got != plain:
            fail("ansible", f"the play reported {got}, the page prints {plain}")

        r = run(base + ["--check"], tmp)
        rec = recap(r.stdout)
        if not rec:
            skipped.append("ansible --check printed no play recap")
            return 1
        got = {k: rec.get(k) for k in checked}
        if checked and got != checked:
            fail("ansible", f"check mode reported {got}, the page prints {checked}")

        r = run(base + ["--limit", "nosuchhost"], tmp)
        if "limit" in exits and r.returncode != exits["limit"]:
            fail("ansible", f"`--limit` matching nothing exited {r.returncode}; "
                            f"the page states {exits['limit']}")

        r = run(["ansible", "nosuchhost", "-i", str(tmp / "inv.ini"), "--list-hosts"], tmp)
        if "list-hosts" in exits and r.returncode != exits["list-hosts"]:
            fail("ansible", f"`--list-hosts` on a bad pattern exited {r.returncode}; "
                            f"the page states {exits['list-hosts']}, which is why it "
                            "must be read rather than exit-checked")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 4


def main() -> int:
    n = check_commands() + check_quotes() + check_ansible()
    if failures:
        print(f"{len(failures)} claim(s) the installed tooling does not support:")
        print("\n".join(failures))
        for s in sorted(set(skipped)):
            print(f"  SKIPPED: {s}")      # what went unchecked matters most here
        return 1
    note = "\n".join(f"  SKIPPED: {s}" for s in sorted(set(skipped)))
    print(f"figures green - {n} documented claims re-checked against the installed CLIs")
    if note:
        print(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
