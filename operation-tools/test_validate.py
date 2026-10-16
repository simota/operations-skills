#!/usr/bin/env python3
"""Prove each rule in validate.py fires.

A check only ever seen passing may be checking nothing. Every rule below gets a
deliberate violation injected into a throwaway copy of the repo, and the test
fails if the validator stays quiet.

Run: make test
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True                     # no __pycache__ in the tools dir
import validate                                    # noqa: E402  — for RULES only


def run(root: Path) -> str:
    r = subprocess.run([sys.executable, str(root / "operation-tools" / "validate.py")],
                       capture_output=True, text=True)
    return r.stdout + r.stderr


def sub(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    assert old in t, f"fixture text not found in {path.name}: {old[:60]!r}"
    path.write_text(t.replace(old, new, 1), encoding="utf-8")


# Each case mutates a copy, then expects a failure line for that rule carrying
# the case's own message fragment. The rule id alone was not enough: a case
# could pass on a different branch of the same rule than the one it was written
# for, and did — V34's "class grants no Bash" case fired on "wrong target".
S = "skills/"

CASES: dict[str, tuple] = {}
QUIET: dict[str, tuple] = {}


def case(rule: str, needle: str):
    def deco(fn):
        CASES[rule] = (fn, needle)
        return fn
    return deco


def quiet(name: str, *rules: str):
    """A mutation that is correct content: the named rules must stay silent.

    This is how a false positive, once fixed, stays fixed."""
    def deco(fn):
        QUIET[name] = (fn, rules)
        return fn
    return deco


def app(path: Path, text: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


def block(text: str, key: str) -> str:
    o, c = f"<!-- deliver:{key} -->", f"<!-- /deliver:{key} -->"
    return o + text.split(o, 1)[1].split(c, 1)[0] + c


@case("V1", '/SKILL.md is ')
def _(r): sub(r / f"{S}operation-runbook/SKILL.md", "## Owns", "## Owns\n" + "x\n" * 200)


@case("V2", "description contains 'Not for'")
def _(r): sub(r / f"{S}operation-runbook/SKILL.md", "Writing reusable procedure that works",
              "Not for operation-incident. Writing reusable procedure that works")


@case("V3", "only on disk=['operation-ghost']")
def _(r): (r / f"{S}operation-ghost").mkdir(); (r / f"{S}operation-ghost/SKILL.md").write_text("x")


@case("V4", 'orphan.md is not linked from Decide first')
def _(r): (r / f"{S}operation-runbook/playbooks/orphan.md").write_text("<!-- operation:guidance -->\n")


@case("V5", 'traps.md is 400 lines')
def _(r): (r / f"{S}operation-runbook/playbooks/traps.md").write_text("y\n" * 400)


@case("V6", '_operation/VALUES.md is')
def _(r): sub(r / f"{S}_operation/VALUES.md", "## 1. Stopping", "z\n" * 200 + "## 1. Stopping")


@case("V7", 'chains operation-nonexistent, which does not exist')
def _(r): sub(r / "operation-registry/routes.yaml", "chain: [operation-oncall, operation-runbook]",
              "chain: [operation-oncall, operation-nonexistent]")


@case("V8", 'links to missing skills/_operation/GONE.md')
def _(r): sub(r / "README.md", "](skills/_operation/CONTRACT.md)", "](skills/_operation/GONE.md)")


@case("V9", 'claimed by both')
def _(r): sub(r / "operation-registry/capabilities.yaml", "signals: [runbook, procedure",
              "signals: [incident, procedure")


@case("V10", 'expected operation-oncall')
def _(r): sub(r / "operation-registry/fixtures.yaml",
              '- ask: "write a runbook for this procedure"\n  expect: operation-runbook',
              '- ask: "write a runbook for this procedure"\n  expect: operation-oncall')


@case("V11", 'skills (max')
def _(r):
    import shutil
    for i in range(4):
        d = r / f"{S}operation-extra{i}"
        d.mkdir()
        shutil.copy(r / f"{S}operation-runbook/SKILL.md", d / "SKILL.md")


@case("V12", 'rogue does not start with')
def _(r): (r / f"{S}rogue").mkdir(); (r / f"{S}rogue/SKILL.md").write_text("x")


@case("V13", 'routes (max')
def _(r):
    t = (r / "operation-registry/routes.yaml").read_text(encoding="utf-8")
    t += "".join(f"\nfiller{i}:\n  pattern: linear\n  when: x\n  chain: [operation-runbook]\n"
                 for i in range(20))
    (r / "operation-registry/routes.yaml").write_text(t, encoding="utf-8")


@case("V13-stages", 'stages (max')
def _(r): sub(r / "operation-registry/routes.yaml", "chain: [operation-oncall, operation-runbook]",
              "chain: [" + ", ".join(["operation-runbook"] * 7) + "]")


@case("V14", "uses pattern 'spiral'")
def _(r): sub(r / "operation-registry/routes.yaml", "  pattern: loop", "  pattern: spiral")


@case("V15", 'allowed-tools is')
def _(r): sub(r / f"{S}operation-readiness/SKILL.md", "allowed-tools: Read, Grep, Glob, Bash",
              "allowed-tools: Read, Grep, Glob, Bash, Write, Edit")


@case("V16", "missing section 'Done when'")
def _(r): sub(r / f"{S}operation-runbook/SKILL.md", "## Done when", "## Finished when")


@case("V17", 'block differs from')
def _(r): sub(r / f"{S}operation-runbook/SKILL.md", "- **Cite the rung inline",
              "- **Mention the rung")


@case("V18", "'toil accounting' is not literal")
def _(r): sub(r / f"{S}operation-runbook/SKILL.md", "toil accounting", "effort tracking")


@case("V19", '`..` does not traverse')
def _(r): sub(r / f"{S}operation-runbook/SKILL.md", "`_operation/CONTRACT.md`", "`../_operation/CONTRACT.md`")


@case("V19-shared", "'SAFETY_TIERS.md', which does not resolve")
def _(r): sub(r / f"{S}_operation/SIZING.md", "`_operation/SAFETY_TIERS.md`", "`SAFETY_TIERS.md`")


@case("V19-reference", "'oncall-health.md', which does not resolve")
def _(r): sub(r / f"{S}operation-oncall/reference/escalation-policy.md",
              "`reference/oncall-health.md`", "`oncall-health.md`")


@case("V20", "defines 'O3'")
def _(r):
    """The definition row becomes a mention; the word is still on the page."""
    sub(r / f"{S}_operation/CONTRACT.md", "| `O3` |", "| O3 |")


@case("V21", 'names no evidence grade')
def _(r): sub(r / f"{S}operation-runbook/SKILL.md",
              """A runbook is `O2` only once it has been executed against a real or staged
system and the observations matched. Reading it back is `O3` — documented, which
evidences that a procedure exists and nothing about whether it works.""",
              "A runbook is proved by running it.")


@case("V22", 'marker carries no residual class')
def _(r): sub(r / f"{S}operation-runbook/SKILL.md", "## Done when",
              "## Done when\n\n#" + "TODO(agent): tidy this up later\n")


@case("V23", 'CONTRACT.md label is')
def _(r): sub(r / f"{S}_operation/CONTRACT.md", "<!-- operation:contract -->", "<!-- operation:guidance -->")


@case("V23-undeclared", "is 'advice', not one of")
def _(r):
    """A label nothing declares, on a pattern no file matches: only the new check can fire."""
    sub(r / "operation-registry/harness.yaml", "label_by_path:\n",
        'label_by_path:\n  "skills/nosuch/*.md": advice\n')


@case("V24", 'names operation-prr, which does not exist')
def _(r): sub(r / f"{S}_operation/ROUTING.md", "`operation-readiness`", "`operation-prr`")


@case("V25", 'pins a version or date')
def _(r): sub(r / f"{S}operation-runbook/playbooks/traps.md", "# ", "# pinned at v2.14.0 — ")


@case("V26", 'sends work to operation-oncall-now')
def _(r): sub(r / "operation-registry/capabilities.yaml", "      go: operation-incident",
              "      go: operation-oncall-now")


@case("V27", 'is a broken symlink')
def _(r):
    (r / f"{S}operation-runbook/_operation").unlink()
    (r / f"{S}operation-runbook/_operation").symlink_to("../_gone")


@case("V28", "prefix is 'operation-'")
def _(r): sub(r / "operation-registry/harness.yaml", "set: operation", "set: ops")


@case("V28-generic-dir", 'registry/ carries no set name')
def _(r): (r / "registry").mkdir()


@case("V29", "has no 'Verified:'")
def _(r):
    f = r / f"{S}operation-runbook/reference/runbook-anatomy.md"
    f.write_text(f.read_text(encoding="utf-8").replace("Verified:", "Checked:"), encoding="utf-8")


@case("V30", 'orphan.md is reachable from nothing')
def _(r): (r / f"{S}operation-runbook/reference/orphan.md").write_text(
    "<!-- operation:deferred -->\n# Orphan\n\nPurpose: x\nRead when: y\nVerified: 2026-08-21\n")


@case("V31", 'states a `Verified:` date and nothing else')
def _(r):
    for f in sorted((r / f"{S}").glob("*/reference/*.md")):
        t = f.read_text(encoding="utf-8")
        i = t.index("Verified:")
        j = t.index("\n\n", i)
        f.write_text(t[:i] + "Verified: 2026-08-21" + t[j:], encoding="utf-8")
        return


@case("V32", "pins its checker to 'claude'")
def _(r):
    sub(r / "operation-registry/routes.yaml", "checker: ", "checker: claude  # ")


@case("V32-unknown", "'nosuchengine', not in")
def _(r):
    sub(r / "operation-registry/routes.yaml", "checker: ", "checker: nosuchengine  # ")



@case("V32-single", "engines.runs_on is ['claude']")
def _(r):
    sub(r / "operation-registry/harness.yaml",
        "runs_on: [claude, codex, agy]", "runs_on: [claude]")



@case("V33", 'declares no refutation lens')
def _(r):
    sub(r / "operation-registry/harness.yaml", "  lens: |", "  lens: ''\n  unused: |")



@case("V34", 'cannot reach it')
def _(r):
    """Reachable and runnable must move together, whichever way they are split."""
    for d in sorted((r / "skills").glob("operation-*")):
        link = d / "refute.py"
        if link.is_symlink():
            link.unlink()                      # runnable, and now out of reach
            return
    # No set-wide link to remove: make a skill runnable instead, and leave it
    # unreachable. Widening a class trips V15 too, which the harness allows —
    # it only asks that V34 appear.
    sub(r / "operation-registry/harness.yaml",
        "tools: \"Read, Grep, Glob, Write", "tools: \"Read, Grep, Glob, Bash, Write")


@case("V34-wrong-target", "not the set's own")
def _(r):
    """A tool link that resolves into the set, but to a different tool."""
    for d in sorted((r / "skills").glob("operation-*")):
        link = d / "refute.py"
        if link.is_symlink():
            link.unlink()
            link.symlink_to("../../operation-tools/render.py")   # the set's own, but the wrong tool
            return


@case("V34-not-named", 'linked_tools[refute.py] does not name it')
def _(r):
    """A link in a skill linked_tools does not name is a grant nobody decided on.

    (Formerly reached only by hoping some class withholds Bash; none here does,
    so the case silently took the wrong-target branch and passed on that.)"""
    sub(r / "operation-registry/harness.yaml", "  refute.py: all", "  refute.py: [operation-change]")


@case("V34-undeclared", 'is a tool link nothing declares')
def _(r):
    """A tool link nothing declares is a capability nobody decided to grant."""
    (r / "skills/operation-runbook/render.py").symlink_to("../../operation-tools/render.py")


@case("V34-missing-tool", 'names nosuch.py')
def _(r): sub(r / "operation-registry/harness.yaml",
              "  refute.py: all", "  refute.py: all\n  nosuch.py: all")


@case("V34-none-declared", 'declares no linked_tools')
def _(r): sub(r / "operation-registry/harness.yaml", "linked_tools:", "unlinked_tools:")


@case("V35", 'never names it in its own words')
def _(r): sub(r / f"{S}operation-runbook/SKILL.md", "and what expires it",
              "and what invalidates it")


@case("V36", 'says nothing about why')
def _(r):
    """An empty required_of has to say why, or the absence is an oversight."""
    h = r / "operation-registry/harness.yaml"
    lines = h.read_text(encoding="utf-8").splitlines(keepends=True)
    out, drop = [], False
    for l in lines:
        if l.startswith("  why:"):
            drop = True
            continue
        if drop and (l.startswith("    ") or not l.strip()):
            continue
        drop = False
        out.append(l)
    h.write_text("".join(out), encoding="utf-8")


@case("V36-none-declared", 'declares no finding_visuals')
def _(r): sub(r / "operation-registry/harness.yaml", "finding_visuals:", "unused_visuals:")


@case("V38", 'switches on KEEP, DROP')
def _(r): sub(r / f"{S}operation-change/playbooks/risk-scoring.md", "## Risk Scoring",
              "verdict: KEEP | DROP\n\n## Risk Scoring")


@case("V37", 'leans on DORA')
def _(r):
    """A page that leans on a declared source and does not say so."""
    sub(r / f"{S}operation-change/reference/dora-metrics.md",
        "Source: DORA — the four keys and their definitions are theirs, not this page's.",
        "Source: none — nothing outside this page can move what it states.")


@case("V37-unused", 'never uses it')
def _(r):
    """A source named in the header that the page never uses."""
    sub(r / f"{S}operation-oncall/reference/onboarding.md",
        "Source: none — nothing outside this page can move what it states.",
        "Source: DORA — the four keys and their definitions are theirs, not this page's.")


@case("V37-silent", 'names no source')
def _(r):
    """Neither a source nor the admission that there is none."""
    sub(r / f"{S}operation-oncall/reference/onboarding.md",
        "Source: none — nothing outside this page can move what it states.", "Source:")


@case("V37-none-declared", 'declares no source_authorities')
def _(r): sub(r / "operation-registry/harness.yaml", "source_authorities:", "unused_authorities:")


# --- branches added or widened by the tooling review -------------------------

RB = f"{S}operation-runbook/SKILL.md"
TRAPS = f"{S}operation-runbook/playbooks/traps.md"


@case("V1-description", "description is")
def _(r): sub(r / RB, "toil accounting.\"", "toil accounting. " + "x" * 120 + "\"")


@case("V1-multiline", "description is")
def _(r):
    """A description continued on a second line is still one description."""
    sub(r / RB, "toil accounting.\"\n", "toil accounting.\n  " + "padding " * 20 + "end.\"\n")


@case("V1-yaml", "frontmatter is not valid YAML")
def _(r): sub(r / RB, "allowed-tools: ", "allowed-tools: [unclosed, ")


@case("V2-multiline", "description contains 'Not for'")
def _(r): sub(r / RB, "toil accounting.\"\n", "toil accounting.\n  Not for paging.\"\n")


@quiet("V4-anchor", "V4", "V8")
def _(r):
    """A Decide-first link to a heading inside a playbook still links the playbook."""
    t = (r / RB).read_text(encoding="utf-8")
    heading = sorted(validate.anchors((r / TRAPS).read_text(encoding="utf-8")))[0]
    assert "](playbooks/traps.md)" in t
    (r / RB).write_text(t.replace("](playbooks/traps.md)", f"](playbooks/traps.md#{heading})", 1),
                        encoding="utf-8")


@case("V5-count", "playbooks (max")
def _(r):
    for i in range(9):
        (r / f"{S}operation-runbook/playbooks/extra{i}.md").write_text("<!-- operation:guidance -->\n")


@case("V6-total", "_operation totals")
def _(r): sub(r / "operation-registry/harness.yaml", "shared_lines_total: 700", "shared_lines_total: 10")


@case("V6-repo", "repo markdown totals")
def _(r): sub(r / "operation-registry/harness.yaml", "repo_md_lines_total: 6300", "repo_md_lines_total: 10")


@case("V8-reference", "links to missing ../_operation/GONE.md")
def _(r): app(r / TRAPS, "\nSee [the gone page][gone].\n\n[gone]: ../_operation/GONE.md\n")


@case("V8-anchor", "has no heading #no-such-heading")
def _(r): app(r / TRAPS, "\nSee [the contract](../_operation/CONTRACT.md#no-such-heading).\n")


@case("V8-scheme", "links to missing httpd-tuning.md")
def _(r): app(r / TRAPS, "\nSee [tuning](httpd-tuning.md).\n")


@quiet("V8-title", "V8")
def _(r):
    app(r / TRAPS, '\nSee [the contract](../_operation/CONTRACT.md "the contract") '
                   "and [it again](<../_operation/CONTRACT.md>).\n")


@quiet("V8-code", "V8")
def _(r):
    """A link quoted as an example, in a fence or a code span, points nowhere."""
    app(r / TRAPS, "\n```markdown\n[x](nowhere.md)\n```\n\nWrite `[x](nowhere.md)` like this.\n")


@case("V14-loop", "is missing max_cycles")
def _(r): sub(r / "operation-registry/routes.yaml", "  max_cycles:", "  xmax_cycles:")


@case("V14-report-only", "is missing stops_at")
def _(r): sub(r / "operation-registry/routes.yaml", "  stops_at:", "  xstops_at:")


@case("V16-fenced", "missing section 'Owns'")
def _(r):
    """A heading quoted in a fence is an example, not the section."""
    sub(r / RB, "## Owns\n", "```markdown\n## Owns\n```\n")


@case("V17-missing", "is missing the values delivery block")
def _(r):
    t = (r / RB).read_text(encoding="utf-8")
    (r / RB).write_text(t.replace(block(t, "values") + "\n", "", 1), encoding="utf-8")


@case("V17-section", "values block is not under 'Decide first'")
def _(r):
    t = (r / RB).read_text(encoding="utf-8")
    b = block(t, "values") + "\n"
    t = t.replace(b, "", 1).replace("## Owns\n", "## Owns\n" + b, 1)
    (r / RB).write_text(t, encoding="utf-8")


@case("V17-duplicate", "carries 2 open and 2 close values markers")
def _(r):
    """A second copy is never compared and never re-rendered."""
    t = (r / RB).read_text(encoding="utf-8")
    c = "<!-- /deliver:values -->"
    (r / RB).write_text(t.replace(c, c + "\n<!-- deliver:values -->\n- stale\n" + c, 1),
                        encoding="utf-8")


@case("V17-format", "sizing block differs from")
def _(r):
    """What `make render` would rewrite fails here, not first in CI."""
    sub(r / RB, "<!-- deliver:sizing -->\n", "<!-- deliver:sizing -->\n\n")


@case("V19-link", "links to '../operation-runbook/SKILL.md'")
def _(r):
    """Resolves from skills/_operation/ in the repo; from an installed skill, nothing."""
    f = r / f"{S}_operation/CONTRACT.md"
    lines = f.read_text(encoding="utf-8").split("\n")
    i = next(i for i, l in enumerate(lines) if l.startswith("# "))
    lines[i] += " — see [runbook](../operation-runbook/SKILL.md)"
    f.write_text("\n".join(lines), encoding="utf-8")


@quiet("V19-reader-paths", "V19")
def _(r):
    """A pattern, and a file in the reader's project, are not this set's paths."""
    app(r / TRAPS, "\nEvery page under `reference/*.md`. Diff the Helm `values.yaml` first.\n")


@case("V19-typo", "'SIZNG.md', which does not resolve")
def _(r):
    """A bare name one letter off an own page is a broken reference, not the reader's file."""
    app(r / TRAPS, "\nRead `SIZNG.md` first.\n")


@case("V19-case", "'contract.md', which does not resolve")
def _(r):
    """A case-only typo resolves on macOS and breaks on Linux."""
    app(r / TRAPS, "\nRead `contract.md` first.\n")


@quiet("V19-near-reader-names", "V19")
def _(r):
    """A reader's file near an own name is not a typo of it."""
    app(r / TRAPS, "\nCheck the Prometheus `rules.yaml` and the team's `deploy-strategy.md`.\n")


@quiet("V19-reader-dirs", "V19")
def _(r):
    """A path into a directory the set does not own is the reader's project."""
    app(r / TRAPS, "\nDiff `config/service.yaml`, `docs/runbook.md`, `scripts/rollback.py` "
                   "and `docs/post-mortem.md`.\n")


@quiet("V8-code-span-heading", "V8")
def _(r):
    """Link syntax inside a code span is literal text in GitHub's anchor."""
    app(r / TRAPS, "\n## Use `[x](y)` syntax\n\n[a](#use-xy-syntax)\n")


@case("V19-swap", "'EXPRIY.md', which does not resolve")
def _(r):
    """A swapped pair in a short page name is a typo, not a reader's file."""
    app(r / TRAPS, "\nRead `EXPRIY.md` first.\n")


@case("V19-case-tool", "'Engine.py', which does not resolve")
def _(r):
    """A case-only typo of an own tool is the set's file too."""
    app(r / TRAPS, "\nRun `Engine.py` first.\n")


@case("V19-upper-ext", "'CONTRACT.MD', which does not resolve")
def _(r): app(r / TRAPS, "\nRead `CONTRACT.MD` first.\n")


@case("V19-missing-dotdot", "'../_operation/CONTRAKT.md'; paths are normalised")
def _(r): app(r / TRAPS, "\nRead `../_operation/CONTRAKT.md` first.\n")


@quiet("V8-footnote", "V8", "V19")
def _(r):
    """A footnote definition is not a link."""
    app(r / TRAPS, "\nThe pager is the floor.[^1]\n\n[^1]: Measured over the last quarter.\n")


@quiet("V8-link-heading", "V8")
def _(r):
    """GitHub drops a link's target from the anchor and decodes a percent-encoded one."""
    app(r / TRAPS, "\n## See [the contract](../_operation/CONTRACT.md) first\n\n## 手順\n\n"
                   "[a](#see-the-contract-first) [b](#%E6%89%8B%E9%A0%86)\n")


@case("V20-column", "defines 'O3'")
def _(r):
    """The word is still in a row, but the row no longer opens with it."""
    sub(r / f"{S}_operation/CONTRACT.md", "| `O3` | Documented |", "| Documented | `O3` |")


@case("V20-elsewhere", "service-tiering.md does not define 'ST0'")
def _(r): sub(r / f"{S}operation-readiness/reference/service-tiering.md", "| `ST0` |", "| ST0 |")


@case("V20-elsewhere-missing", "which does not exist")
def _(r): sub(r / "operation-registry/harness.yaml",
              "service_tiers: operation-readiness/reference/service-tiering.md",
              "service_tiers: operation-readiness/reference/nosuch.md")


@case("V22-beside-code", "marker carries no residual class")
def _(r):
    """Code elsewhere on the line does not make the marker a quotation."""
    sub(r / TRAPS, "# ", "#" + "TODO(agent): rerun `make figures` and fix this later\n# ")


@case("V24-hyphen", "names operation-on-call, which does not exist")
def _(r): sub(r / f"{S}_operation/ROUTING.md", "`operation-readiness`",
              "`operation-readiness` / `operation-on-call`")


@case("V27-outside", "points outside the repo")
def _(r):
    (r / f"{S}operation-runbook/_operation").unlink()
    (r / f"{S}operation-runbook/_operation").symlink_to(Path(r.anchor).resolve())


@case("V27-nested", "operation-runbook/reference/escape points outside the repo")
def _(r): (r / f"{S}operation-runbook/reference/escape").symlink_to(Path(r.anchor).resolve())


@case("V34-nested", "below the skill's top level")
def _(r): (r / f"{S}operation-runbook/playbooks/refute.py").symlink_to(
    "../../../operation-tools/refute.py")


@case("V35-vocabulary", "never defines 'proved'")
def _(r):
    f = r / f"{S}_operation/EXPIRY.md"
    f.write_text(f.read_text(encoding="utf-8").replace("`proved`", "proved"), encoding="utf-8")


@case("V36-required", "which does not exist")
def _(r): sub(r / "operation-registry/harness.yaml", "required_of: []", "required_of: [operation-runbook]")


@case("V37-hyphen", "leans on DORA")
def _(r): app(r / f"{S}operation-oncall/reference/alert-hygiene.md",
              "\nScore the rotation with DORA-style change failure rate.\n")


RISK = f"{S}operation-change/playbooks/risk-scoring.md"


@case("V38-digits", "switches on ST9")
def _(r): sub(r / RISK, "## Risk Scoring", "tier: ST0 | ST9\n\n## Risk Scoring")


@case("V38-backticks", "switches on MAYBE")
def _(r): sub(r / RISK, "## Risk Scoring", "verdict: `GO` | `MAYBE`\n\n## Risk Scoring")


@case("V38-trailing", "switches on MAYBE")
def _(r): sub(r / RISK, "## Risk Scoring", "verdict: GO | MAYBE (pick one).\n\n## Risk Scoring")


@case("V38-list", "switches on KEEP, DROP")
def _(r): sub(r / RISK, "## Risk Scoring", "- KEEP | DROP\n\n## Risk Scoring")


# --- the other tools ----------------------------------------------------------
# Not rules, so not counted against validate.RULES; each guards a defect that
# was reproduced and fixed, and each runs in seconds with no engine installed.

def _copy() -> tuple:
    tmp = tempfile.TemporaryDirectory()
    copy = Path(tmp.name) / "repo"
    shutil.copytree(ROOT, copy, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return tmp, copy


def tool_render_refuses_broken_markers() -> str:
    tmp, copy = _copy()
    with tmp:
        f = copy / RB
        t = f.read_text(encoding="utf-8").replace("<!-- /deliver:values -->\n", "", 1)
        f.write_text(t, encoding="utf-8")
        r = subprocess.run([sys.executable, str(copy / "operation-tools/render.py")],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return "render.py exited 0 on a missing close marker"
        if f.read_text(encoding="utf-8") != t:
            return "render.py rewrote a file whose markers it refused"
    return ""


def tool_engine_requires_running() -> str:
    tmp = tempfile.TemporaryDirectory()
    with tmp:
        p, s = Path(tmp.name) / "p.txt", Path(tmp.name) / "s.json"
        p.write_text("x")
        s.write_text("{}")
        r = subprocess.run([sys.executable, str(ROOT / "operation-tools/engine.py"), "codex",
                            "--prompt-file", str(p), "--schema", str(s)],
                           capture_output=True, text=True)
        if r.returncode != 2 or "--running is required" not in r.stderr:
            return f"engine.py without --running exited {r.returncode}: {r.stderr.strip()[:200]}"
        # A misspelt running engine must not let the named checker be the maker.
        r = subprocess.run([sys.executable, str(ROOT / "operation-tools/engine.py"), "claude",
                            "--running", "cluade", "--prompt-file", str(p), "--schema", str(s)],
                           capture_output=True, text=True)
        if r.returncode == 0 or "is not one of" not in r.stderr:
            return f"engine.py accepted --running cluade (exit {r.returncode})"
        return ""


def tool_engine_checks_schema() -> str:
    import engine
    schema = {"type": "object", "properties": {"refuted": {"type": "boolean"},
              "why": {"anyOf": [{"type": "object", "properties": {}}, {"type": "null"}]}},
              "required": ["refuted"]}
    bad = [{}, {"refuted": "yes"}, {"refuted": True, "extra": 1}, {"refuted": True, "why": {"x": 1}}]
    for v in bad:
        if not engine.conforms(v, engine.strict(schema)):
            return f"engine.conforms accepted {v}"
    if engine.conforms({"refuted": False, "why": None}, engine.strict(schema)):
        return "engine.conforms rejected a valid answer"
    # oneOf means exactly one; allOf means every one.
    if not engine.conforms(3, {"oneOf": [{"type": "integer"}, {"type": "number"}]}):
        return "engine.conforms accepted a value matching two oneOf branches"
    if not engine.conforms({"a": 1}, {"allOf": [{"required": ["a"]}, {"required": ["b"]}]}):
        return "engine.conforms ignored an allOf branch"
    # enum/const hold instance values, not schemas: strict() must leave them alone.
    if engine.strict({"enum": [{"type": "object"}]}) != {"enum": [{"type": "object"}]}:
        return "engine.strict rewrote an enum value as if it were a schema"
    if not engine.conforms([], {"type": "array", "contains": {"type": "object"}}):
        return "engine.conforms accepted an empty array against `contains`"
    try:
        engine.run("codex", "x", {"type": "object", "properties": {"a": {"type": "string",
                                  "minLength": 2}}})
        return "engine.run accepted a schema with a keyword conforms cannot verify"
    except engine.EngineError as e:
        if "cannot verify" not in str(e):
            return f"engine.run refused the schema for the wrong reason: {e}"
    cond = {"if": {"type": "object", "properties": {"k": {"const": "a"}}},
            "then": {"type": "object", "properties": {"r": {"type": "string"}}}}
    if engine.strict(cond) != cond:
        return "engine.strict closed an `if`/`then` branch, which changes what it matches"
    inner = engine.strict({"type": "array", "contains": {"type": "object"}})["contains"]
    if inner.get("additionalProperties") is not False:
        return "engine.strict left an object under `contains` open"
    return ""


def tool_engine_dash_prompt() -> str:
    """A prompt opening with `-` reaches the engine as the prompt, not as an option."""
    import engine
    tmp = tempfile.TemporaryDirectory()
    with tmp:
        d = Path(tmp.name)
        fake = d / "claude"
        fake.write_text("#!/bin/sh\nprintf '%s\\n' \"$2\" > \"$(dirname \"$0\")/argv\"\n"
                        "echo '{\"structured_output\": {\"ok\": true}}'\n")
        fake.chmod(0o755)
        old = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{d}:{old}"
        try:
            engine.run("claude", "- check the rollback", {"type": "object",
                       "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]})
        finally:
            os.environ["PATH"] = old
        sent = (d / "argv").read_text()
        if sent.startswith("-"):
            return f"engine passed a dash-leading prompt as {sent[:30]!r}, read as an option"
    return ""


def tool_refute_unchecked_fails() -> str:
    tmp = tempfile.TemporaryDirectory()
    with tmp:
        c = Path(tmp.name) / "claims.json"
        c.write_text('[{"id": "c1", "claim": "x"}]')
        r = subprocess.run([sys.executable, str(ROOT / "operation-tools/refute.py"),
                            "--running", "claude", str(c)], capture_output=True, text=True,
                           env={"PATH": tmp.name, "HOME": tmp.name})
        if r.returncode != 1 or "[UNCHECKED]" not in r.stdout or "Traceback" in r.stderr:
            return f"refute.py with no engine exited {r.returncode}: {(r.stdout + r.stderr)[-200:]}"
        return ""


def tool_figures_parsing() -> str:
    import figures_check as fc
    got = fc.subcommand_words("aws", "--profile prod ec2 describe-instances".split())
    if got[:2] != ["ec2", "describe-instances"]:
        return f"figures_check read `aws --profile prod ec2` as {got[:2]}"
    if fc.norm("a command-specific format") != fc.norm(
            fc.re.sub(r"(\w)-[ \t]*\n\s*(\w)", r"\1\2", "a command-\nspecific format")):
        return "figures_check compares a real hyphen differently from a typeset break"
    return ""


TOOL_CHECKS = [tool_render_refuses_broken_markers, tool_engine_requires_running,
               tool_engine_dash_prompt,
               tool_engine_checks_schema, tool_refute_unchecked_fails, tool_figures_parsing]


def _run_case(mutate) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "repo"
        shutil.copytree(ROOT, copy, symlinks=True,
                        ignore=shutil.ignore_patterns(".git", "__pycache__"))
        mutate(copy)
        return run(copy)


def main() -> int:
    baseline = run(ROOT)
    if "green" not in baseline:
        print("the working tree is already failing; fix that first:\n" + baseline)
        return 1

    bad: list[str] = []
    for rule, (mutate, needle) in CASES.items():
        out = _run_case(mutate)
        expect = rule.split("-")[0]
        if not re.search(rf"^\s*{expect}: .*{re.escape(needle)}", out, re.M):
            bad.append(rule)
            print(f"  {rule} did not fire with {needle!r}\n{out}")
    for name, (mutate, rules) in QUIET.items():
        out = _run_case(mutate)
        # Silence from a crash is not silence: the validator has to have finished.
        if "Traceback" in out or not re.search(r"^(green|\d+ failure\(s\))$", out, re.M):
            bad.append(name)
            print(f"  {name}: the validator did not finish\n{out}")
            continue
        loud = [l.strip() for l in out.splitlines()
                if any(re.match(rf"\s*{r}: ", l) for r in rules)]
        if loud:
            bad.append(name)
            print(f"  {name} should leave {', '.join(rules)} silent:\n    " + "\n    ".join(loud))
    for check in TOOL_CHECKS:
        why = check()
        if why:
            bad.append(check.__name__)
            print(f"  {check.__name__}: {why}")

    total = len(CASES) + len(QUIET) + len(TOOL_CHECKS)
    print(f"{len(CASES)} firing cases, {len(QUIET)} quiet cases, "
          f"{len(TOOL_CHECKS)} tool checks; {len(bad)} wrong")
    if bad:
        print("wrong: " + ", ".join(bad))
        return 1

    # Counting the cases that exist says nothing about the rules that do. A rule
    # added without a case left this printing "every rule fires" about it.
    covered = {c.split("-")[0] for c in CASES}
    declared = {fn.__name__.split("_")[0].upper() for fn in validate.RULES}
    untested = sorted(declared - covered, key=lambda r: int(r[1:]))
    if untested:
        print("no deliberate violation is injected for: " + ", ".join(untested))
        return 1
    print(f"every rule fires ({len(declared)} rules, {total} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
