#!/usr/bin/env python3
"""Static checks over the operation-* skill set.

Every threshold and every piece of vocabulary comes from operation-registry/harness.yaml.
Nothing is hard-coded here: a number written twice is a number that drifts.

A rule earns its place only if CI can decide it. Anything needing judgement
belongs in a review, not in this file.
"""
from __future__ import annotations

import difflib
import os
import re
import sys
import urllib.parse
import unicodedata
from pathlib import Path

import yaml

from fences import fence_step       # stdlib-only, so figures_check can share it

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def fail(rule: str, msg: str) -> None:
    FAILURES.append(f"{rule}: {msg}")


# --- what the corpus is --------------------------------------------------------

_IGNORED: set[str] | None = None


def _ignored() -> set[str]:
    """Paths git ignores here, directories ending in `/`. Only when this tree is
    a repository's own top level: the pre-commit snapshot or a test copy holds
    only what was meant to be checked, and may sit inside some other repository
    (a TMPDIR under a dotfiles repo that ignores `*`) whose rules must not empty
    the corpus — that would pass every commit unchecked."""
    global _IGNORED
    if _IGNORED is None:
        import subprocess
        _IGNORED = set()
        try:
            top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=ROOT,
                                 capture_output=True, text=True, timeout=30)
            if top.returncode == 0 and Path(top.stdout.strip()).resolve() == ROOT.resolve():
                r = subprocess.run(["git", "ls-files", "-z", "--others", "--ignored",
                                    "--exclude-standard", "--directory"], cwd=ROOT,
                                   capture_output=True, text=True, timeout=30)
                if r.returncode == 0:
                    _IGNORED = set(filter(None, r.stdout.split("\0")))
        except (OSError, subprocess.TimeoutExpired):
            pass
    return _IGNORED


def excluded(path: Path) -> bool:
    """Not part of the corpus: git's own directory, anything .gitignore covers
    (`.operations/` is where these skills write their artifacts), or a nested
    repository such as a worktree. CI and the hook never see those, so counting
    them locally turns a green tree red."""
    if path.name == ".git":
        return True
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        return False
    if path.is_dir():
        return rel + "/" in _ignored() or (path != ROOT and (path / ".git").exists())
    return rel in _ignored()


def corpus(base: Path, pattern: str = "*.md") -> list[Path]:
    """Every file under `base` matching `pattern`, without the excluded trees."""
    out = []
    for d, dirs, files in os.walk(base):
        dirs[:] = sorted(x for x in dirs if not excluded(Path(d) / x))
        out += [Path(d) / f for f in files
                if Path(f).match(pattern) and not excluded(Path(d) / f)]
    return sorted(out)


# --- corpus ------------------------------------------------------------------

def load(name: str):
    with (ROOT / "operation-registry" / name).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


H = load("harness.yaml")
CAP = load("capabilities.yaml")
ROUTES = load("routes.yaml")
FIX = load("fixtures.yaml")

LIM = H["limits"]
VOCAB = H["vocabulary"]
PREFIX = H["prefix"]
SET = H["set"]
SHARED = H["shared_dir"]
CONTRACT_FILE = f"{SHARED}/CONTRACT.md"
ROUTING_FILE = f"{SHARED}/ROUTING.md"
SIGNATURE = H["signature"]
PLATFORM_DIRS = set(H["platform_dirs"])

SKILLS_ROOT = ROOT / H["skills_dir"] if H.get("skills_dir") else ROOT
SKILL_DIRS = sorted(p for p in SKILLS_ROOT.glob(f"{PREFIX}*") if (p / "SKILL.md").exists())
SKILLS = [p.name for p in SKILL_DIRS]
# Link text may hold one level of brackets — `[the [old] page](x.md)`, or an
# image inside a link, whose own target IMAGE_RE then reads. Bracketed text
# followed by `(` is a link of its own, and CommonMark lets the inner one win:
# in `[a [b](x.md) c](y.md)` the link is x.md.
LINK_RE = re.compile(r"\[(?:[^\[\]]|!\[[^\[\]]*\]|\[[^\[\]]*\](?!\())+\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[[^\[\]]*\]\(([^)]+)\)")
# A backticked token is a path if it contains a slash or names a file. Matching
# only on the slash misses the bare sibling reference (`SIZING.md`), which is
# the form that breaks: it resolves against the skill directory, not against
# the directory the file writing it lives in.
TICK_PATH_RE = re.compile(r"`([^`\s]*(?:/[^`\s]*|\.(?i:md|yaml|py)))`")
MARKER_RE = re.compile(r"#" + r"TODO\(agent\):")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


FRONTMATTER_ERROR = "__error__"


def frontmatter(text: str) -> dict:
    """The frontmatter as YAML reads it, which is how every host reads it.

    A line-by-line reading saw only the first line of a description that runs
    onto a second one, so a 500-character description passed the length check.
    Lists are joined the way `allowed-tools` is written as a string.
    """
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {FRONTMATTER_ERROR: "no closing ---"}
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        return {FRONTMATTER_ERROR: " ".join(str(e).split())}
    if not isinstance(data, dict):
        return {FRONTMATTER_ERROR: "not a mapping"}
    return {str(k): ", ".join(map(str, v)) if isinstance(v, list) else
            ("" if v is None else str(v)) for k, v in data.items()}


def unfenced(text: str) -> list[tuple[int, str]]:
    """(line number, line) for every line outside a fenced code block."""
    out, fence = [], None
    for i, line in enumerate(text.splitlines(), 1):
        fence, edge = fence_step(line, fence)
        if fence is None and not edge:
            out.append((i, line))
    return out


def sections(text: str) -> dict[str, str]:
    """`## ` headings outside code fences. A heading quoted in an example is not one."""
    out, cur, buf, fence = {}, None, [], None
    for line in text.splitlines():
        fence, edge = fence_step(line, fence)
        if fence is None and not edge and line.startswith("## "):
            if cur:
                out[cur] = "\n".join(buf)
            cur, buf = line[3:].strip(), []
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf)
    return out


CODE_SPAN_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
# `[^1]: ...` is a footnote, not a link definition.
REF_DEF_RE = re.compile(r"^\s{0,3}\[(?!\^)[^\]]+\]:\s*(\S+)")


def _link_target(raw: str) -> str:
    """The path in `(target "title")` or `(<target>)`, as CommonMark reads it."""
    t = raw.strip()
    if t.startswith("<") and ">" in t:
        return t[1:t.index(">")]
    return re.sub(r"""\s+(?:"[^"]*"|'[^']*'|\([^)]*\))\s*$""", "", t)


def links(text: str) -> list[str]:
    """Every link target outside code: inline links and reference definitions."""
    out = []
    for _, line in unfenced(text):
        # A code span becomes a placeholder, not nothing: `[`x`](y)` is still a
        # link, and `` `[x](y)` `` no longer is one.
        line = CODE_SPAN_RE.sub("code", line)
        found = LINK_RE.findall(line)
        found += [m for m in IMAGE_RE.findall(line) if m not in found]
        out += [_link_target(m) for m in found]
        m = REF_DEF_RE.match(line)
        if m:
            out.append(_link_target(m.group(1)))
    return out


def is_external(target: str) -> bool:
    return bool(SCHEME_RE.match(target))


def slug(heading: str) -> str:
    """GitHub's heading anchor: lower case, punctuation dropped, spaces to hyphens."""
    # One pass, so link syntax inside a code span stays literal text, as GitHub keeps it.
    h = re.sub(r"(`+)(.+?)\1|!?\[([^\]]*)\]\([^)]*\)",
               lambda m: m.group(2) if m.group(1) else m.group(3), heading.strip()).lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(text: str) -> set[str]:
    seen: dict[str, int] = {}
    out = set()
    for _, line in unfenced(text):
        m = re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if not m:
            continue
        s = slug(m.group(1))
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    out |= set(re.findall(r"""<a\s+(?:name|id)=["']([^"']+)["']""", text))
    return out


FIXED_SECTIONS = ["Owns", "Before starting", "Decide first",
                  "Always / Never", "Verify with", "Done when"]


# --- rules -------------------------------------------------------------------

def v1_sizes():
    for d in SKILL_DIRS:
        t = read(d / "SKILL.md")
        n = len(t.splitlines())
        if n > LIM["skill_md_lines"]:
            fail("V1", f"{d.name}/SKILL.md is {n} lines (max {LIM['skill_md_lines']})")
        fm = frontmatter(t)
        if FRONTMATTER_ERROR in fm:
            fail("V1", f"{d.name}/SKILL.md frontmatter is not valid YAML "
                       f"({fm[FRONTMATTER_ERROR]}); no host can read its description")
        desc = fm.get("description", "")
        if len(desc) > LIM["description_chars"]:
            fail("V1", f"{d.name} description is {len(desc)} chars "
                       f"(max {LIM['description_chars']}; the listing truncates)")


def v2_description_terms():
    others = set(SKILLS)
    for d in SKILL_DIRS:
        desc = frontmatter(read(d / "SKILL.md")).get("description", "")
        for term in H["forbidden_description_terms"]:
            if term in desc:
                fail("V2", f"{d.name} description contains {term!r}; "
                           "boundaries belong in capabilities.yaml `not:`")
        for name in others - {d.name}:
            if name in desc:
                fail("V2", f"{d.name} description names {name}")


def v3_roster():
    declared = set(k for k in CAP if k.startswith(PREFIX))
    if declared != set(SKILLS):
        fail("V3", f"capabilities.yaml vs disk: only in yaml={sorted(declared - set(SKILLS))} "
                   f"only on disk={sorted(set(SKILLS) - declared)}")


def v4_playbook_orphans():
    for d in SKILL_DIRS:
        pb_dir = d / "playbooks"
        if not pb_dir.exists():
            continue
        body = sections(read(d / "SKILL.md")).get("Decide first", "")
        linked = {Path(m.split("#")[0]).name for m in links(body)}
        for pb in sorted(pb_dir.glob("*.md")):
            if pb.name not in linked:
                fail("V4", f"{d.name}/playbooks/{pb.name} is not linked from Decide first")


def v5_playbook_budget():
    for d in SKILL_DIRS:
        pbs = sorted((d / "playbooks").glob("*.md")) if (d / "playbooks").exists() else []
        if len(pbs) > LIM["playbooks_per_skill"]:
            fail("V5", f"{d.name} has {len(pbs)} playbooks (max {LIM['playbooks_per_skill']})")
        for pb in pbs:
            n = len(read(pb).splitlines())
            if n > LIM["playbook_lines"]:
                fail("V5", f"{pb.relative_to(ROOT)} is {n} lines (max {LIM['playbook_lines']})")


def v6_budgets():
    total = 0
    for f in sorted((SKILLS_ROOT / SHARED).glob("*.md")):
        n = len(read(f).splitlines())
        total += n
        if n > LIM["shared_file_lines"]:
            fail("V6", f"{SHARED}/{f.name} is {n} lines (max {LIM['shared_file_lines']})")
    if total > LIM["shared_lines_total"]:
        fail("V6", f"{SHARED} totals {total} lines (max {LIM['shared_lines_total']})")
    repo = sum(len(read(f).splitlines()) for f in corpus(ROOT))
    if repo > LIM["repo_md_lines_total"]:
        fail("V6", f"repo markdown totals {repo} lines (max {LIM['repo_md_lines_total']})")


def v7_routes_real():
    for name, r in ROUTES.items():
        for s in r.get("chain", []):
            if s not in SKILLS:
                fail("V7", f"route {name} chains {s}, which does not exist")


def v8_links():
    """Every link resolves, and so does the heading it points at.

    Reference definitions count as links, a title or angle brackets around the
    target do not make it a different file, and a link quoted in code is an
    example rather than a pointer.
    """
    cache: dict[Path, set[str]] = {}
    for f in corpus(ROOT):
        for target in links(read(f)):
            if not target or is_external(target):
                continue
            path, _, frag = target.partition("#")
            dest = f.parent / path if path else f
            if not dest.exists():
                fail("V8", f"{f.relative_to(ROOT)} links to missing {target}")
                continue
            if frag and dest.suffix == ".md" and dest.is_file():
                key = dest.resolve()
                if key not in cache:
                    cache[key] = anchors(read(dest))
                if urllib.parse.unquote(frag).lower() not in cache[key]:
                    fail("V8", f"{f.relative_to(ROOT)} links to {target}, and "
                               f"{path or f.name} has no heading #{frag}")


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s).lower()


def v9_signals():
    seen: dict[str, str] = {}
    for name, c in CAP.items():
        sigs = c.get("signals", [])
        if not sigs:
            fail("V9", f"{name} declares no signals")
        for s in sigs:
            k = _norm(s)
            if k in seen:
                fail("V9", f"signal {s!r} claimed by both {seen[k]} and {name}")
            seen[k] = name


def v10_fixtures():
    pairs = [(_norm(s), name) for name, c in CAP.items() for s in c.get("signals", [])]
    if not isinstance(FIX, list) or not FIX:
        fail("V10", "fixtures.yaml is not a non-empty list of asks; this rule is checking nothing")
        return
    for entry in FIX:
        ask, expect = _norm(entry["ask"]), entry["expect"]
        hits = [(len(sig), owner) for sig, owner in pairs if sig in ask]
        if not hits:
            fail("V10", f"no signal matches {entry['ask']!r} (expected {expect})")
            continue
        best = max(h[0] for h in hits)
        winners = {owner for ln, owner in hits if ln == best}
        if winners != {expect}:
            fail("V10", f"{entry['ask']!r} -> {sorted(winners)}, expected {expect}")


def v11_count():
    if len(SKILLS) > LIM["skills_max"]:
        fail("V11", f"{len(SKILLS)} skills (max {LIM['skills_max']}); "
                    "past the cap an addition must retire one")


def v12_prefix():
    for d in SKILLS_ROOT.iterdir():
        if d.is_dir() and (d / "SKILL.md").exists() and not d.name.startswith(PREFIX):
            fail("V12", f"{d.name} does not start with {PREFIX!r}")


def v13_route_budget():
    if len(ROUTES) > LIM["routes_max"]:
        fail("V13", f"{len(ROUTES)} routes (max {LIM['routes_max']})")
    for name, r in ROUTES.items():
        stages = len(r.get("chain", []))
        if stages > LIM["route_stages_max"]:
            fail("V13", f"route {name} chains {stages} stages (max {LIM['route_stages_max']})")


def v14_patterns():
    for name, r in ROUTES.items():
        p = r.get("pattern")
        if p not in VOCAB["patterns"]:
            fail("V14", f"route {name} uses pattern {p!r}, not in the vocabulary")
        if p == "loop":
            for key in ("oracle", "checker", "max_cycles"):
                if key not in r:
                    fail("V14", f"loop route {name} is missing {key}")
        if p == "report-only" and "stops_at" not in r:
            fail("V14", f"report-only route {name} is missing stops_at")


def v15_permission_class():
    classes = H["permission_classes"]
    for d in SKILL_DIRS:
        declared = CAP.get(d.name, {}).get("class")
        if declared not in classes:
            fail("V15", f"{d.name} declares unknown class {declared!r}")
            continue
        want = classes[declared]["tools"]
        got = frontmatter(read(d / "SKILL.md")).get("allowed-tools", "")
        if got != want:
            fail("V15", f"{d.name} allowed-tools is {got!r}, class {declared} requires {want!r}")


def v16_sections():
    for d in SKILL_DIRS:
        have = sections(read(d / "SKILL.md"))
        for s in FIXED_SECTIONS:
            if s not in have:
                fail("V16", f"{d.name}/SKILL.md is missing section {s!r}")


def v17_delivery():
    for key, spec in H["delivered"].items():
        want = read(ROOT / "operation-registry" / "delivered" / f"{key}.md").rstrip("\n")
        open_m, close_m = f"<!-- deliver:{key} -->", f"<!-- /deliver:{key} -->"
        for d in SKILL_DIRS:
            text = read(d / "SKILL.md")
            if open_m not in text or close_m not in text:
                fail("V17", f"{d.name}/SKILL.md is missing the {key} delivery block")
                continue
            # One block, in order. A second copy is never compared and never
            # re-rendered, so it is the one that goes stale.
            n_open, n_close = text.count(open_m), text.count(close_m)
            if n_open != 1 or n_close != 1 or text.index(open_m) > text.index(close_m):
                fail("V17", f"{d.name}/SKILL.md carries {n_open} open and {n_close} close "
                            f"{key} markers; exactly one block, opened before it is closed")
                continue
            # Byte-for-byte what render.py writes. A looser comparison passed a
            # block that `make render` then rewrites, which is green locally and
            # red in CI's render-and-diff step.
            got = text.split(open_m, 1)[1].split(close_m, 1)[0]
            if got != f"\n{want}\n":
                fail("V17", f"{d.name}/SKILL.md {key} block differs from "
                            f"operation-registry/delivered/{key}.md (run: make render)")
            body = sections(text).get(spec["section"], "")
            if open_m not in body:
                fail("V17", f"{d.name}/SKILL.md {key} block is not under {spec['section']!r}")


def v18_signals_in_description():
    for d in SKILL_DIRS:
        desc = _norm(frontmatter(read(d / "SKILL.md")).get("description", ""))
        for s in CAP.get(d.name, {}).get("signals", []):
            if _norm(s) not in desc:
                fail("V18", f"{d.name} signal {s!r} is not literal in its description; "
                            "the listing carries nothing else")


def v19_paths_resolve():
    """Every path a skill can be told to read must resolve from its own directory.

    A skill is handed its own directory as the base, and paths are normalised
    lexically, so `..` never travels back through the install symlink. That
    applies to the shared contracts too — they are read *by* a skill, so a
    sibling-relative path in them points at nothing once installed.
    """
    probe = SKILL_DIRS[0]
    shared = sorted((SKILLS_ROOT / SHARED).glob("*.md"))
    for d in SKILL_DIRS:
        # reference/ is read by the skill exactly as playbooks/ is, so a bare
        # sibling name there (`oncall-health.md`) breaks the same way.
        readable = [d / "SKILL.md"]
        for sub in ("playbooks", "reference"):
            readable += sorted((d / sub).glob("*.md"))
        for f in readable:
            _check_paths(f, d, f"{d.name}/{f.relative_to(d)}")
            _check_links(f, d / f.relative_to(d), f"{d.name}/{f.relative_to(d)}")
    for f in shared:                      # checked once, against one skill dir
        _check_paths(f, probe, f"{SHARED}/{f.name}")
        _check_links(f, probe / SHARED / f.name, f"{SHARED}/{f.name}")


def _check_links(f: Path, seen_as: Path, label: str) -> None:
    """A markdown link is followed from where the skill sees the file.

    V8 resolves a link from the file's place in this repository, where
    `_operation/../operation-runbook/` happens to exist. Read through a skill's
    `_operation` symlink and normalised lexically, the same link lands inside
    that skill and points at nothing.
    """
    for target in links(read(f)):
        path = target.partition("#")[0]
        if not path or is_external(path):
            continue
        lexical = Path(os.path.normpath(os.path.join(str(seen_as.parent), path)))
        if not lexical.exists():
            fail("V19", f"{label} links to {path!r}, which resolves lexically to "
                        f"{lexical.relative_to(SKILLS_ROOT) if SKILLS_ROOT in lexical.parents else lexical} "
                        "once read from a skill directory, and nothing is there")


# A backticked path is a reference to this set only if it sits under one of the
# set's own roots, or names a file this set has. `node_modules/` in a search
# playbook, or a Helm `values.yaml`, is the reader's project, not a pointer into
# this repo. A bare `SIZING.md` still counts: the set has one, and from a
# playbook that name resolves to nothing.
_OWN_NAMES: set[str] = set()


def _own_names() -> set[str]:
    if not _OWN_NAMES:
        for top in (SKILLS_ROOT, ROOT / f"{SET}-registry", ROOT / f"{SET}-tools"):
            for d, dirs, files in os.walk(top):
                dirs[:] = [x for x in dirs if not excluded(Path(d) / x)]
                _OWN_NAMES.update(dirs)
                _OWN_NAMES.update(f for f in files if not excluded(Path(d) / f))
    return _OWN_NAMES


def _own_roots() -> set[str]:
    """The first path segments that can only mean this set."""
    roots = {SHARED, "registry", "playbooks", "reference", H.get("skills_dir") or "skills"}
    roots |= {d.name for d in ROOT.iterdir() if d.is_dir() and d.name.startswith(PREFIX)}
    return roots | set(SKILLS)


def _is_own_reference(p: str) -> bool:
    if any(p.startswith(x) or p == x for x in H.get("external_paths", [])):
        return False
    if any(c in p for c in "*?["):
        return False                      # a pattern, not a path
    if p.startswith((f"{SHARED}/", "registry/", "playbooks/", "reference/")):
        return True
    if not p.lower().endswith((".md", ".yaml", ".py")):
        return False
    if ".." in p or p.startswith("./"):
        return True                       # relative to the file: check it resolves
    if "/" in p:
        # A path into one of the set's own roots is the set's; any other directory
        # (`config/service.yaml`, `docs/post-mortem.md`) is the reader's project,
        # unless the file at its end is exactly one of the set's names — no typo
        # matching there, since a reader's file may well resemble a page.
        if p.split("/", 1)[0] in _own_roots():
            return True
        return p.rsplit("/", 1)[1].lower() in {n.lower() for n in _own_names()}
    # A name is the set's when the set has it, or is a typo of one of its pages:
    # `SIZNG.md`, `contract.md`. Only pages are near-matched — a reader's
    # `rules.yaml` is not a typo of `routes.yaml` — at 0.85, which still catches a
    # swapped pair in a short name (`EXPRIY.md`); and a plural or singular of a
    # page (`deploy-strategy.md`) is a different word, not a misspelling.
    if p.lower() in {n.lower() for n in _own_names()}:
        return True                       # exact, or case only: resolves on macOS, not on Linux
    pages = {n.lower() for n in _own_names() if n.endswith(".md")}
    near = difflib.get_close_matches(p.lower(), pages, n=1, cutoff=0.85)
    return bool(near) and _stem(near[0]) != _stem(p)


def _stem(name: str) -> str:
    """`deploy-strategies.md` and `deploy-strategy.md` share a stem, and so do
    `processes.md` and `process.md` — but not `proces.md`, a typo of the latter."""
    s = name.lower().rsplit(".", 1)[0]
    if s.endswith("ies"):
        return s[:-3] + "y"
    if s.endswith("sses"):
        return s[:-2]
    return s if s.endswith("ss") else s.removesuffix("s")


def _check_paths(f: Path, base: Path, label: str) -> None:
    for p in TICK_PATH_RE.findall(read(f)):
        if p.startswith(("http", "~", "/")) or " " in p or not _is_own_reference(p):
            continue
        if ".." in p:
            fail("V19", f"{label} references {p!r}; paths are normalised lexically, "
                        "so `..` does not traverse the install symlink")
        elif not (base / p).exists():
            fail("V19", f"{label} references {p!r}, which does not resolve from a "
                        "skill directory")


# A definition, as against a mention: a table row or a heading that opens with
# the word. `patterns` and `checkers` are route vocabulary and live in
# routes.yaml, so no page is asked to define them.
# Matched per line: the row has to open with the word, the heading has to be one.
DEFINITION_FORMS = (r"^\s*\|\s*`{w}`\s*\|", r"^\s*\|\s*`\[{w}\]`\s*\|", r"^#{{2,6}}\s+`{w}`")
ROUTE_VOCAB = {"patterns", "checkers"}


def v20_contract_vocabulary():
    """Every declared word is defined on a shared page, not merely named there.

    The earlier form asked whether the word appeared anywhere in CONTRACT.md,
    and a word used in a sentence passed as defined — the check §5.7 of
    `agent-toolkit`'s DESIGN.md names, that one replaced definition does not trip. A definition is a row or a
    heading, and every vocabulary key is held to it, not three.
    """
    shared = {p.name: read(p) for p in (SKILLS_ROOT / SHARED).glob("*.md")}
    elsewhere = H.get("vocabulary_defined_in") or {}
    for key, words in VOCAB.items():
        if key in ROUTE_VOCAB:
            continue
        if key in elsewhere:
            page = SKILLS_ROOT / elsewhere[key]
            if not page.is_file():
                fail("V20", f"vocabulary_defined_in[{key}] names {elsewhere[key]}, "
                            "which does not exist")
                continue
            pages, where = {page.name: read(page)}, f"{elsewhere[key]} does not define"
        else:
            pages, where = shared, f"no page under {SHARED}/ defines"
        for word in words:
            forms = [re.compile(f.format(w=re.escape(word)), re.M) for f in DEFINITION_FORMS]
            if not any(f.search(t) for t in pages.values() for f in forms):
                fail("V20", f"{where} {word!r} ({key}) — "
                            "a table row or a heading, not a mention")


def strip_delivered(text: str) -> str:
    for key in H["delivered"]:
        text = re.sub(rf"<!-- deliver:{key} -->.*?<!-- /deliver:{key} -->",
                      "", text, flags=re.S)
    return text


def v21_verify_names_a_grade():
    for d in SKILL_DIRS:
        body = strip_delivered(sections(read(d / "SKILL.md")).get("Verify with", ""))
        if not any(g in body for g in VOCAB["evidence_levels"]):
            fail("V21", f"{d.name} Verify with names no evidence grade of its own; "
                        "the delivered block does not count")


def v22_markers_classified():
    for f in corpus(ROOT):
        if f.parts[-2:-1] == ("delivered",):
            continue
        for i, line in enumerate(read(f).splitlines(), 1):
            # A marker quoted in code is a mention; one beside code is still a marker.
            if MARKER_RE.search(CODE_SPAN_RE.sub("", line)):
                if not any(c in line for c in VOCAB["residual_classes"]):
                    fail("V22", f"{f.relative_to(ROOT)}:{i} marker carries no residual class")


def v23_labels():
    import fnmatch
    allowed = set(H["document_labels"])
    for pat, label in H["label_by_path"].items():
        if label not in allowed:
            fail("V23", f"label_by_path[{pat!r}] is {label!r}, not one of {sorted(allowed)}")
    for f in corpus(ROOT):
        rel = str(f.relative_to(ROOT))
        want = None
        for pat, label in H["label_by_path"].items():
            if fnmatch.fnmatch(rel, pat):
                want = label
                break
        if want is None:
            continue
        lines = read(f).splitlines()
        if lines and lines[0].strip() == "---":          # skip frontmatter
            end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), 0)
            lines = lines[end + 1:]
        first = next((l for l in lines if l.strip()), "")
        if first.strip() != f"<!-- {SET}:{want} -->":
            fail("V23", f"{rel} label is {first.strip()!r}, expected {SET}:{want}")


def v24_rendered_tables():
    routing = read(SKILLS_ROOT / ROUTING_FILE)
    readme = read(ROOT / "README.md")
    for name in SKILLS:
        if f"`{name}`" not in routing:
            fail("V24", f"{ROUTING_FILE} does not list {name}")
        if name not in readme:
            fail("V24", f"README.md does not list {name}")
    for doc, text in ((SKILLS_ROOT / ROUTING_FILE, routing), (ROOT / "README.md", readme)):
        for found in set(re.findall(rf"`({re.escape(PREFIX)}[a-z0-9-]+)`", text)):
            if found not in SKILLS and not (ROOT / found).is_dir():
                fail("V24", f"{doc.relative_to(ROOT)} names {found}, which does not exist")


def v25_playbook_rot():
    pats = [re.compile(p) for p in H["rot_patterns"]]
    for d in SKILL_DIRS:
        for pb in sorted((d / "playbooks").glob("*.md")) if (d / "playbooks").exists() else []:
            for i, line in enumerate(read(pb).splitlines(), 1):
                for p in pats:
                    if p.search(line):
                        fail("V25", f"{pb.relative_to(ROOT)}:{i} pins a version or date; "
                                    "content that goes stale belongs outside the budget")


def v26_boundaries_real():
    for name, c in CAP.items():
        for entry in c.get("not", []):
            go = entry.get("go", "")
            if go.startswith(PREFIX) and go not in SKILLS:
                fail("V26", f"{name} `not:` sends work to {go}, which does not exist")


def v27_symlinks_stay_inside():
    """What a skill reaches must live in this repo, and must actually be there.

    At any depth: a link under playbooks/ or reference/ is read the same way as
    one at the top. The walk does not follow links, so `_operation` and
    `registry` are checked as links and not descended into.
    """
    for d in SKILL_DIRS:
        for entry in skill_entries(d):
            if not entry.is_symlink():
                continue
            rel = entry.relative_to(d)
            target = (entry.parent / os.readlink(entry)).resolve()
            if not target.exists():
                fail("V27", f"{d.name}/{rel} is a broken symlink")
            elif ROOT.resolve() not in target.parents and target != ROOT.resolve():
                fail("V27", f"{d.name}/{rel} points outside the repo ({target})")


def skill_entries(d: Path) -> list[Path]:
    """Every file, directory and link under a skill, without following links."""
    out = []
    for top, dirs, files in os.walk(d, followlinks=False):
        out += [Path(top) / n for n in sorted(dirs + files)]
    return sorted(out)


def v28_namespace_agrees():
    """One declaration, and every namespaced name derived from it.

    A skills directory is flat and shared with every other set on the machine,
    so the names that travel there carry the set and the names that do not
    travel stay inside a skill directory.
    """
    if PREFIX != f"{SET}-":
        fail("V28", f"prefix is {PREFIX!r}; set {SET!r} requires {SET + '-'!r}")
    if SHARED != f"_{SET}":
        fail("V28", f"shared_dir is {SHARED!r}; set {SET!r} requires {'_' + SET!r}")
    if not (SKILLS_ROOT / SHARED).is_dir():
        fail("V28", f"{SHARED}/ does not exist")
    # Every directory this set owns carries the set name. The alternative rule —
    # "prefix only what gets installed" — needs a judgement about what travels,
    # and a sibling set's install line (`cp -R operation-* _common <skills dir>`)
    # is what that judgement looks like when it is wrong.
    for d in sorted(list(ROOT.iterdir()) + list(SKILLS_ROOT.iterdir() if SKILLS_ROOT != ROOT else [])):
        if not d.is_dir() or d.name in PLATFORM_DIRS or excluded(d):
            continue
        if not (d.name.startswith(PREFIX) or d.name == SHARED):
            fail("V28", f"{d.name}/ carries no set name; a directory this set owns "
                        f"is {PREFIX}* or {SHARED}, so that copying it into a shared "
                        "skills directory cannot collide")


def v29_reference_headers():
    """reference/ carries no line budget, so it carries headers instead.

    A file with no stated purpose and no date of last check is indistinguishable
    from one that is still true, which is how a deferred layer rots quietly.
    """
    want = H["reference_headers"]
    for d in SKILL_DIRS:
        for f in sorted((d / "reference").glob("*.md")) if (d / "reference").exists() else []:
            head = "\n".join(read(f).splitlines()[:12])
            for header in want:
                if header not in head:
                    fail("V29", f"{f.relative_to(ROOT)} has no {header!r} in its first "
                                "12 lines; the deferred layer states what it claims "
                                "and when anyone last checked")


def v30_reference_orphans():
    """A reference nothing points at is never read and never noticed as stale."""
    for d in SKILL_DIRS:
        ref_dir = d / "reference"
        if not ref_dir.exists():
            continue
        body = sections(read(d / "SKILL.md")).get("Decide first", "")
        linked = {Path(m.split("#")[0]).name for m in links(body)}
        for pb in sorted((d / "playbooks").glob("*.md")) if (d / "playbooks").exists() else []:
            linked |= {Path(m.split("#")[0]).name for m in links(read(pb))}
            linked |= {Path(m).name for m in TICK_PATH_RE.findall(read(pb))}
        for f in sorted(ref_dir.glob("*.md")):
            if f.name not in linked:
                fail("V30", f"{f.relative_to(ROOT)} is reachable from nothing — "
                            "not the Decide first table, not a playbook")


def v31_verified_names_a_check():
    """A `Verified:` date cannot fail, so the line has to say what can.

    Either it names what re-checks the page, or it says that nothing does. Both
    are acceptable; what is not is a bare date, which reads exactly like a
    checked page and is indistinguishable from one that has rotted.
    """
    markers = H.get("verified_markers")
    if not markers:
        fail("V31", "harness.yaml declares no verified_markers; this rule is checking nothing")
        return
    for d in SKILL_DIRS:
        for f in sorted((d / "reference").glob("*.md")) if (d / "reference").exists() else []:
            lines = read(f).splitlines()
            start = next((i for i, l in enumerate(lines) if l.startswith("Verified:")), None)
            if start is None:
                continue                      # V29 already reports the missing header
            block = []
            for l in lines[start:]:
                if not l.strip():
                    break
                block.append(l)
            text = " ".join(block)
            if not any(m in text for m in markers):
                fail("V31", f"{f.relative_to(ROOT)} states a `Verified:` date and nothing "
                            "else; name what re-checks it, or say `no automated check`")

def v32_checker_engine():
    """A loop route's checker is resolved against the engine that is running.

    `checker: external` checked nothing. Naming an engine instead was no better:
    all three CLIs read this SKILL.md, so a checker pinned to `codex` is the
    maker marking its own work on any run that is codex. What can be checked
    here is that the set names more than one engine — otherwise no run has an
    independent one to reach for — and that the route defers the choice.
    """
    eng = H.get("engines") or {}
    runs_on = eng.get("runs_on") or []
    if len(runs_on) < 2:
        fail("V32", f"engines.runs_on is {runs_on}; with fewer than two engines no "
                    "run can be checked by one that did not produce the work")
    allowed = VOCAB.get("checkers") or []
    if not allowed:
        fail("V32", "harness.yaml declares no checker vocabulary; "
                    "this rule is checking nothing")
        return
    for name, r in ROUTES.items():
        if r.get("pattern") != "loop":
            continue
        c = r.get("checker")
        if c in runs_on:
            fail("V32", f"loop route {name} pins its checker to {c!r}; on a run that "
                        f"is {c!r} that is the maker marking its own work")
        elif c not in allowed:
            fail("V32", f"loop route {name} checks with {c!r}, not in {allowed}")


def v33_refutation_lens():
    """The set says what a refuting engine should attack, and what breaks a claim.

    `refute.py` is identical in every set; the lens is what makes it adversarial
    rather than a second opinion, and it is the one part that cannot be shared.
    A set holding the tool and no framing would ask two engines to review — which
    is the thing an adversarial pass exists to not be.
    """
    r = H.get("refutation") or {}
    for key in ("lens", "refuted_when"):
        if not (r.get(key) or "").strip():
            fail("V33", f"harness.yaml declares no refutation {key}; "
                        f"{SET}-tools/refute.py has nothing domain-specific to ask with")


def v34_tools_reachable():
    """Every declared tool is reachable from a skill exactly where it is runnable.

    Linked into a skill whose class withholds `Bash`, a tool is decoration that
    reads like a capability. Missing from one that holds `Bash`, the skill has to
    shell out to a path outside its own directory, which does not resolve. Tying
    the link to the grant makes the absence checked rather than accidental — a set
    where no skill can run one says so out loud.

    The list is `linked_tools` in harness.yaml, so adding a tool costs one line
    and is checked the same way as the ones already there. The tools directory is
    never linked whole: a skill holding `Bash` and all of it could edit the
    harness it is part of, `render.py` included.
    """
    declared_tools = H.get("linked_tools") or {}
    if not declared_tools:
        fail("V34", "harness.yaml declares no linked_tools; this rule is "
                    "checking nothing")
        return
    for tool, who in declared_tools.items():
        source = ROOT / f"{SET}-tools" / tool
        if not source.exists():
            fail("V34", f"linked_tools names {tool}, which is not in {SET}-tools/")
            continue
        wanted = set(SKILLS) if who == "all" else set(who)
        unknown = wanted - set(SKILLS)
        if unknown:
            fail("V34", f"linked_tools[{tool}] names {sorted(unknown)}, "
                        "which are not skills")
        for d in SKILL_DIRS:
            cls = CAP.get(d.name, {}).get("class")
            has_shell = "Bash" in H["permission_classes"].get(cls, {}).get("tools", "")
            link = d / tool
            should = d.name in wanted and has_shell
            if should and not link.is_symlink():
                fail("V34", f"{d.name} may run {SET}-tools/{tool} but cannot reach "
                            f"it; link it as {tool}")
            if not should and link.is_symlink():
                why = ("its class grants no Bash" if d.name in wanted
                       else f"linked_tools[{tool}] does not name it")
                fail("V34", f"{d.name} links {tool} and {why}")
            if link.is_symlink() and link.resolve() != source.resolve():
                fail("V34", f"{d.name}/{tool} points at {link.resolve()}, not "
                            "the set's own")
    for d in SKILL_DIRS:
        for entry in skill_entries(d):
            if entry.suffix != ".py":
                continue
            rel = entry.relative_to(d)
            if entry.parent != d:
                fail("V34", f"{d.name}/{rel} is a tool below the skill's top level; "
                            "a tool is linked at the top, where linked_tools checks it")
            elif entry.name not in declared_tools:
                fail("V34", f"{d.name}/{rel} is a tool link nothing "
                            "declares; add it to linked_tools or remove it")


def v35_signature():
    """The mechanism this set has and its siblings do not, checked the same way.

    Each set declares one signature mechanism in `signature:` — the contract
    that carries it, the vocabulary it introduces, and the skills that owe it.
    The rule is identical in every set; only the declaration differs, which is
    what keeps the copies of this file from becoming dialects.

    The delivered block states the rule inside every skill. A skill that owes
    the mechanism also names its own half of it, because a rule stated
    everywhere and owned nowhere is a ritual.
    """
    contract = f"{SHARED}/{SIGNATURE['contract']}"
    path = SKILLS_ROOT / contract
    if not path.exists():
        fail("V35", f"signature names {contract}, which does not exist")
        return
    text = read(path)
    for word in VOCAB[SIGNATURE["vocabulary"]]:
        if f"`{word}`" not in text:
            fail("V35", f"{contract} never defines {word!r}, which "
                        f"{SIGNATURE['vocabulary']} declares")
    for name in SIGNATURE["required_of"]:
        if name not in SKILLS:
            fail("V35", f"signature.required_of names {name!r}, which is not a skill")
            continue
        body = strip_delivered(read(SKILLS_ROOT / name / "SKILL.md"))
        if SIGNATURE["own_word"] not in body:
            fail("V35", f"{name} owes the {SIGNATURE['name']} mechanism and never names "
                        f"it in its own words; the delivered block does not count")


def v36_finding_visuals():
    """A finding a reader has to reassemble gets a picture, and the picture is
    held to the same standard as the words.

    `finding_visuals` in harness.yaml names the triggers, the forms and the
    floor; this checks the review skill actually defines each of them, and that
    its `Decide first` table reaches the playbook — a rule stated in a file
    nothing links to is read on no launches at all.

    A set with no review skill declares `required_of: []` and says why. The
    absence is then a decision on the record rather than something a later
    reader has to notice.
    """
    fv = H.get("finding_visuals")
    if not fv:
        fail("V36", "harness.yaml declares no finding_visuals; this rule is "
                    "checking nothing")
        return
    required = fv.get("required_of")
    if required is None:
        fail("V36", "finding_visuals declares no required_of")
        return
    if not required:
        if not (fv.get("why") or "").strip():
            fail("V36", "finding_visuals.required_of is empty and says nothing "
                        "about why no skill in this set owes a diagram")
        return
    words = list(fv.get("triggers") or []) + list(fv.get("floor") or [])
    if not words or not fv.get("forms"):
        fail("V36", "finding_visuals declares no triggers, floor or forms; "
                    "the rule would check that a file exists and nothing else")
        return
    for name in required:
        if name not in SKILLS:
            fail("V36", f"finding_visuals.required_of names {name!r}, "
                        "which is not a skill")
            continue
        pb = SKILLS_ROOT / name / "playbooks" / fv["playbook"]
        ref = SKILLS_ROOT / name / "reference" / fv["contract"]
        for f in (pb, ref):
            if not f.exists():
                fail("V36", f"{name} owes {f.relative_to(SKILLS_ROOT)}, "
                            "which does not exist")
        if not (pb.exists() and ref.exists()):
            continue
        text = read(pb) + read(ref)
        for word in words:
            if f"`{word}`" not in text:
                fail("V36", f"{name} never defines {word!r}, which "
                            "finding_visuals declares")
        for form in fv["forms"]:
            if form not in _norm(text):
                fail("V36", f"{name} never names the {form!r} form")
        body = sections(read(SKILLS_ROOT / name / "SKILL.md")).get("Decide first", "")
        if fv["playbook"] not in body:
            fail("V36", f"{name}/SKILL.md does not reach {fv['playbook']} from "
                        "Decide first; a rule nothing links to is read on no launches")


def v37_source_pins_the_rot():
    """`Verified:` is when someone looked. `Source:` is what they looked at.

    V31 makes the line name what re-checks it, and across the family 94 of 114
    reference pages answer `no automated check`. That one admission covers two
    populations: pages bound to something outside themselves, and the templates
    and catalogues that depend on nothing and cannot go stale. Only the first
    can rot, and nothing in the header said which page was which.

    So the header names it and the check is an equality — every authority the
    registry declares and the body leans on is named in `Source:`, and nothing
    is named there the body does not use. Where the registry pins a version,
    that version has to appear in the page too: a page edited to a newer one
    then fails instead of quietly disagreeing with its own header.

    Nothing here reads a date or leaves the machine. Freshness is time- and
    environment-dependent and does not belong in CI; agreement between a header
    and its own body is neither.

    Matching is on word boundaries, not substrings. Plain `in` reported that a
    page on test oracles depended on git, having found it inside "legitimate".
    """
    def names(text: str, name: str) -> bool:
        # A hyphen joins a modifier, not a different name: `DORA-style` leans on
        # DORA as much as `DORA` does.
        return re.search(rf"(?<![\w]){re.escape(name)}(?![\w])", text) is not None

    declared = H.get("source_authorities")
    none_marker = H.get("source_none_marker")
    if declared is None or not none_marker:
        fail("V37", "harness.yaml declares no source_authorities/source_none_marker; "
                    "this rule is checking nothing. A set whose reference layer "
                    "depends on nothing outside itself declares the map empty — "
                    "silence and emptiness have to look different")
        return
    for d in SKILL_DIRS:
        for f in sorted((d / "reference").glob("*.md")) if (d / "reference").exists() else []:
            lines = read(f).splitlines()
            start = next((i for i, l in enumerate(lines) if l.startswith("Source:")), None)
            if start is None:
                continue                      # V29 already reports the missing header
            # The block ends at the next header, not at the next blank line.
            # `Source:` and `Verified:` sit on adjacent lines, and a run-to-blank
            # reading swallowed the evidence line into the header — where it named
            # the very tool the mutation had just removed, and the rule stayed
            # quiet about a page that no longer declared what it runs on.
            end = start
            while (end + 1 < len(lines) and lines[end + 1].strip()
                   and not any(lines[end + 1].startswith(h) for h in H["reference_headers"])):
                end += 1
            head = " ".join(lines[start:end + 1])
            body = "\n".join(lines[:start] + lines[end + 1:])
            named = [a for a in declared if names(head, a)]
            if not named and none_marker not in head:
                fail("V37", f"{f.relative_to(ROOT)} names no source and does not say "
                            f"{none_marker!r}; a page that depends on nothing says so, "
                            "because silence reads the same from a page that rots")
            for name, version in declared.items():
                if names(body, name) and not names(head, name):
                    fail("V37", f"{f.relative_to(ROOT)} leans on {name} and its `Source:` "
                                "does not name it; the header is where the rot is declared")
                if names(head, name) and not names(body, name):
                    fail("V37", f"{f.relative_to(ROOT)} names {name} in `Source:` and never "
                                "uses it; a source the page does not depend on pins nothing")
                if version and names(head, name):
                    pin = f"{name} {version}"
                    if pin not in head:
                        fail("V37", f"{f.relative_to(ROOT)} names {name} in `Source:` without "
                                    f"the pinned version; the registry pins {version}, and a "
                                    "source without one cannot be compared with anything later")
                    elif pin not in body:
                        fail("V37", f"{f.relative_to(ROOT)} pins {pin} and the page never says "
                                    f"{pin}; one of the two moved without the other")


# `KEY: A | B | C` in a schema, or a bare `A | B | C` on a line of its own (or a
# list item) — upper-case words, digits allowed after the first letter, each
# optionally in backticks, joined by pipes, with a closing period or a
# parenthetical allowed after. Underscored and lower-case forms are not
# matched, so this is a floor.
_ENUM_WORD = r"`?[A-Z][A-Z0-9-]*(?: [A-Z][A-Z0-9-]*)*`?"
ENUM_RE = re.compile(rf"(?:^\s*(?:[-*+]\s+)?|:\s*)({_ENUM_WORD}(?:\s*\|\s*{_ENUM_WORD})+)"
                     r"(?:\s*\([^)]*\))?\s*[.,;]?\s*(?:#.*)?$")


def v38_enumerations_declared():
    """A value set a page switches on is declared vocabulary, or nothing checks it.

    `SEVERITY: CRITICAL | HIGH | MEDIUM | LOW | NIT` in a handoff schema is a
    vocabulary — the receiver branches on it — and a set that writes it only
    on the page has no rule reaching it, so `low` in a playbook fails nowhere.
    Declared words are what V20 and V22 reach; the rest is what drifts.
    """
    declared = {w for words in VOCAB.values() for w in words}
    for f in corpus(SKILLS_ROOT):
        for i, line in enumerate(read(f).splitlines(), 1):
            m = ENUM_RE.search(line)
            if not m:
                continue
            words = [w.strip().strip("`") for w in m.group(1).split("|")]
            missing = [w for w in words if w not in declared]
            if missing:
                fail("V38", f"{f.relative_to(ROOT)}:{i} switches on {', '.join(missing)}, "
                            "which harness.yaml vocabulary does not declare")


RULES = [v1_sizes, v2_description_terms, v3_roster, v4_playbook_orphans,
         v5_playbook_budget, v6_budgets, v7_routes_real, v8_links, v9_signals,
         v10_fixtures, v11_count, v12_prefix, v13_route_budget, v14_patterns,
         v15_permission_class, v16_sections, v17_delivery,
         v18_signals_in_description, v19_paths_resolve, v20_contract_vocabulary,
         v21_verify_names_a_grade, v22_markers_classified, v23_labels,
         v24_rendered_tables, v25_playbook_rot, v26_boundaries_real,
         v27_symlinks_stay_inside, v28_namespace_agrees,
         v29_reference_headers, v30_reference_orphans, v31_verified_names_a_check,
         v32_checker_engine,
         v33_refutation_lens,
         v34_tools_reachable,
         v35_signature,
         v36_finding_visuals,
         v37_source_pins_the_rot,
         v38_enumerations_declared]


def hook_installed() -> bool:
    """Where git looks for hooks: a worktree's `.git` is a file, and
    core.hooksPath moves them elsewhere. Run from the hook itself, this is a
    snapshot of the index outside any repository — and the hook is plainly on."""
    import subprocess
    if os.environ.get("OPERATION_PRECOMMIT") == "1":
        return True
    try:
        r = subprocess.run(["git", "rev-parse", "--git-path", "hooks"], cwd=ROOT,
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return False
    if r.returncode != 0 or not r.stdout.strip():
        return False
    # On only when it is this repo's hook, and git can run it: any file at that
    # path is not the same thing, and a foreign hook is left alone by `make hooks`.
    # Compared by content: a linked worktree shares the hook with another checkout.
    import filecmp
    hook = ROOT / r.stdout.strip() / "pre-commit"
    ours = ROOT / "operation-tools/githooks/pre-commit"
    return (hook.exists() and os.access(hook, os.X_OK)
            and filecmp.cmp(hook, ours, shallow=False))


def main() -> int:
    for rule in RULES:
        rule()
    hooks = hook_installed()
    print(f"{len(RULES)} rules · {len(SKILLS)} skills · "
          f"hooks {'on' if hooks else 'off — run: make hooks'}")
    if FAILURES:
        for f in sorted(FAILURES):
            print(f"  {f}")
        print(f"\n{len(FAILURES)} failure(s)")
        return 1
    print("green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
