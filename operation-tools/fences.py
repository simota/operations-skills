"""Where a Markdown code fence opens and closes, read as CommonMark reads it.

Standard library only: validate.py and figures_check.py both import it, and
`make figures` runs without the validator's dependencies or its registry.
"""
from __future__ import annotations      # `str | None` on Python 3.9

import re

FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")


def fence_step(line: str, fence: str | None) -> tuple[str | None, bool]:
    """The open fence after `line`, and whether `line` itself opened or closed one.

    As CommonMark reads it: a fence closes only on a run of the same character,
    at least as long, with nothing after it. A ```` fence quoting a ``` example,
    or a ```bash line inside a ``` block, is content, not the end of the block.
    """
    m = FENCE_RE.match(line)
    if not m:
        return fence, False
    run, rest = m.group(1), m.group(2)
    if fence is None:
        if run[0] == "`" and "`" in rest:      # inline code, not a fence
            return None, False
        return run, True
    if run[0] == fence[0] and len(run) >= len(fence) and not rest.strip():
        return None, True
    return fence, False
