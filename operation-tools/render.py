#!/usr/bin/env python3
"""Write the delivered blocks back into every SKILL.md.

A contract kept only in the shared directory is not read on most launches, so the operative
part is carried verbatim in each skill. That only stays true if changing one
line does not cost one hand edit per skill — this is that cost, paid once.

Idempotent: run it, commit the diff.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
from fences import Fences                 # noqa: E402  — the same reading validate's sections() uses

ROOT = Path(__file__).resolve().parent.parent
H = yaml.safe_load((ROOT / "operation-registry" / "harness.yaml").read_text(encoding="utf-8"))
PREFIX = H["prefix"]
SKILLS_ROOT = ROOT / H["skills_dir"] if H.get("skills_dir") else ROOT


class RenderError(Exception):
    """A SKILL.md whose markers cannot be rendered without guessing."""


def heading_lines(lines: list[str]):
    """(index, line) of every `## ` heading outside a fence."""
    f = Fences()
    for i, line in enumerate(lines):
        edge = f.step(line.rstrip("\n"))
        if f.fence is None and not edge and line.startswith("## "):
            yield i, line


def render(path: Path) -> bool:
    """Rewrite each delivered block in place. Raises rather than guess.

    A missing close marker used to send this down the insert path, which added
    a second block; the next run then replaced everything from the orphaned
    open marker to the new close — deleting whatever the author had written in
    between. Any marker count other than none-and-none or one-and-one, in
    order, is refused and the file is left as it was.
    """
    text = path.read_text(encoding="utf-8")
    original = text
    for key, spec in H["delivered"].items():
        block = (ROOT / "operation-registry" / "delivered" / f"{key}.md").read_text(
            encoding="utf-8").rstrip("\n")
        open_m, close_m = f"<!-- deliver:{key} -->", f"<!-- /deliver:{key} -->"
        payload = f"{open_m}\n{block}\n{close_m}"
        n_open, n_close = text.count(open_m), text.count(close_m)
        if (n_open, n_close) == (1, 1) and text.index(open_m) < text.index(close_m):
            head, rest = text.split(open_m, 1)
            _, tail = rest.split(close_m, 1)
            text = head + payload + tail
        elif (n_open, n_close) == (0, 0):
            heading = f"## {spec['section']}"
            # The heading is a whole line: `### Done when` contains `## Done when`,
            # and matching it put the block into a subsection of another section.
            # Both ends are read outside fences, as V17 reads them: a `## Timeline`
            # in a fenced postmortem skeleton ended the section, and the block
            # landed inside the example.
            lines = text.splitlines(keepends=True)
            starts = [i for i, l in heading_lines(lines)]
            at = next((i for i in starts if lines[i].rstrip("\n") == heading), None)
            if at is None:
                raise RenderError(f"{path.parent.name}/SKILL.md has no section "
                                  f"{spec['section']!r} to deliver {key} into")
            # append at the end of that section, before the next heading
            nxt = next((i for i in starts if i > at), len(lines))
            head, body, tail = "".join(lines[:at]), "".join(lines[at + 1:nxt]), "".join(lines[nxt:])
            text = (head + heading + "\n" + body.rstrip("\n") + "\n" + payload + "\n"
                    + ("\n" + tail if tail else ""))
        else:
            raise RenderError(f"{path.parent.name}/SKILL.md has {n_open} open and "
                              f"{n_close} close {key} markers; fix them by hand — "
                              "rendering would overwrite whatever lies between")
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed, errors = [], []
    for d in sorted(SKILLS_ROOT.glob(f"{PREFIX}*")):
        if not (d / "SKILL.md").exists():
            continue
        try:
            if render(d / "SKILL.md"):
                changed.append(d.name)
        except RenderError as e:
            errors.append(str(e))
    print(f"rendered: {len(changed)} changed" + (f" ({', '.join(changed)})" if changed else ""))
    for e in errors:
        print(f"  {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
