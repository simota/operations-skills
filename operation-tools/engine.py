#!/usr/bin/env python3
"""Run a checker on an engine that did not produce the work.

`routes.yaml` defers every loop route's `checker` to run time, because all three
CLIs read the same SKILL.md and any of them may be the one running. This resolves
it: given the engine that is running, it picks one that is not.

    make engines                     every declared engine answers, or says why
    python3 operation-tools/engine.py --running claude --prompt-file p.txt --schema s.json

**The running engine is stated, never sniffed.** codex launched from inside
Claude Code inherits `CLAUDECODE` and `CLAUDE_CODE_*`, so a nested run reads as
its parent and any env heuristic silently mis-identifies it — which would hand
back a verdict from the very engine that was supposed to be excluded. `--running`
is required, and absent it this stops.

**A checker that did not run is not a checker that passed.** Every failure path
here raises. Nothing returns a default verdict, nothing degrades to "assume
fine": an engine missing from PATH, an engine that starts and produces no
parseable object, a response that does not match the schema — each is an error
with the engine's own words attached, because the alternative is a green run
that verified nothing (`DESIGN.md` §5.4b in the `agent-toolkit` repository).

Engine quirks, re-checked by `make engines` rather than dated:

* `codex exec` rejects a schema without `additionalProperties: false`, at every
  level. Schemas are normalised here so callers write ordinary JSON Schema.
* `agy --print` returns an envelope; the validated object is `structured_output`.
* `claude -p --json-schema` validates on the engine's side, like agy; the
  validated object is `structured_output` in the JSON envelope, and its absence
  is an error.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
H = yaml.safe_load((ROOT / "operation-registry" / "harness.yaml").read_text(encoding="utf-8"))
ENGINES = H.get("engines") or {}
TIMEOUT = 600


class EngineError(RuntimeError):
    """The engine did not answer. Never a verdict."""


def strict(schema: dict) -> dict:
    """Every object closed, which is what codex requires and agy tolerates.

    Including the ones under `anyOf` / `oneOf` / `allOf` and `$defs`, which are
    lists or maps of schemas rather than a schema.
    """
    if isinstance(schema, list):
        return [strict(s) for s in schema]
    if not isinstance(schema, dict):
        return schema
    out = {k: strict(v) if isinstance(v, (dict, list)) else v for k, v in schema.items()}
    for key in ("$defs", "definitions"):
        if isinstance(schema.get(key), dict):
            out[key] = {k: strict(v) for k, v in schema[key].items()}
    if out.get("type") == "object":
        out["additionalProperties"] = False
        out["properties"] = {k: strict(v) for k, v in (out.get("properties") or {}).items()}
    if isinstance(out.get("items"), dict):
        out["items"] = strict(out["items"])
    return out


_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool,
          "null": type(None), "number": (int, float), "integer": int}


def conforms(value, schema: dict, where: str = "$") -> list[str]:
    """What in `value` breaks `schema`: the subset these tools write, checked
    here because an engine's own validation is a claim, not an observation."""
    if not isinstance(schema, dict):
        return []
    for key in ("anyOf", "oneOf"):
        if isinstance(schema.get(key), list):
            if all(conforms(value, s, where) for s in schema[key]):
                return [f"{where}: matches none of {key}"]
    errs = []
    t = schema.get("type")
    if t is not None:
        names = t if isinstance(t, list) else [t]
        ok = False
        for name in names:
            py = _TYPES.get(name)
            if py is None:
                continue
            if isinstance(value, bool) and name in ("number", "integer"):
                continue                      # True is an int in Python, not in JSON
            if isinstance(value, py):
                ok = True
        if not ok:
            return [f"{where}: expected {t}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{where}: {value!r} is not one of {schema['enum']}")
    if isinstance(value, dict):
        props = schema.get("properties") or {}
        for k in schema.get("required") or []:
            if k not in value:
                errs.append(f"{where}: missing required {k!r}")
        for k, v in value.items():
            if k in props:
                errs += conforms(v, props[k], f"{where}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{where}: unexpected property {k!r}")
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for i, v in enumerate(value):
            errs += conforms(v, schema["items"], f"{where}[{i}]")
    return errs


def run(engine: str, prompt: str, schema: dict) -> dict:
    """Ask `engine` for one object matching `schema`. Raises rather than guessing.

    The answer is checked against the schema here as well: a well-formed object
    with the wrong keys is not an answer, and passing it on turned into a
    KeyError three frames later in whoever read the verdict.
    """
    got = _ask(engine, prompt, schema)
    errs = conforms(got, strict(schema))
    if errs:
        raise EngineError(f"{engine} answered, but not in the schema: "
                          + "; ".join(errs[:5]) + f"\n{json.dumps(got)[:400]}")
    return got


def _ask(engine: str, prompt: str, schema: dict):
    known = ENGINES.get("runs_on") or []
    if engine not in known:
        raise EngineError(f"{engine} is not one of {known}")

    with tempfile.TemporaryDirectory(prefix="operation-engine-") as tmp:
        d = pathlib.Path(tmp)
        s = d / "schema.json"
        s.write_text(json.dumps(strict(schema)), encoding="utf-8")
        if engine == "codex":
            out = d / "answer.json"
            argv = ["codex", "exec", "--output-schema", str(s), "-o", str(out),
                    "--sandbox", "read-only", "--skip-git-repo-check", prompt]
            r = _spawn(engine, argv)
            body = out.read_text(encoding="utf-8") if out.exists() else ""
            if not body.strip():
                raise EngineError(f"codex wrote no answer.\n{_tail(r)}")
            return _parse(engine, body)
        if engine == "claude":
            argv = ["claude", "-p", prompt, "--output-format", "json",
                    "--json-schema", json.dumps(strict(schema))]
            r = _spawn(engine, argv)
            envelope = _parse(engine, r.stdout)
            if "structured_output" not in envelope:
                raise EngineError(f"claude returned no structured_output "
                                  f"(subtype {envelope.get('subtype')!r}).\n{_tail(r)}")
            return envelope["structured_output"]
        if engine == "agy":
            argv = ["agy", f"--print={prompt}", "--output-format", "json",
                    "--json-schema", str(s)]
            r = _spawn(engine, argv)
            envelope = _parse(engine, r.stdout)
            if "structured_output" not in envelope:
                raise EngineError(f"agy returned no structured_output "
                                  f"(status {envelope.get('status')!r}).\n{_tail(r)}")
            return envelope["structured_output"]
    raise EngineError(f"no invocation is known for {engine}")


def _spawn(engine: str, argv: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT)
    except FileNotFoundError:
        raise EngineError(f"{engine} is not on PATH") from None
    except OSError as e:
        # E2BIG on a prompt past the per-argument limit, EACCES on a
        # non-executable file on PATH: the engine did not run, which is an
        # EngineError like any other, not a traceback that ends the whole pass.
        raise EngineError(f"{engine} could not be started: {e}") from None
    except subprocess.TimeoutExpired:
        raise EngineError(f"{engine} did not answer within {TIMEOUT}s") from None


def _parse(engine: str, body: str) -> dict:
    stripped = body.strip()
    try:
        got = json.loads(stripped)
        if isinstance(got, dict):
            return got
    except ValueError:
        pass
    for line in reversed(stripped.splitlines()):
        try:
            got = json.loads(line)
        except ValueError:
            continue
        if isinstance(got, dict):
            return got
    raise EngineError(f"{engine} printed nothing that parses as an object:\n{body[:400]}")


def _tail(r: subprocess.CompletedProcess) -> str:
    return "\n".join((r.stderr or r.stdout or "").strip().splitlines()[-6:])


def other_than(running: str) -> str:
    """An engine that is not the one running. Raises rather than falling back."""
    known = ENGINES.get("runs_on") or []
    if running not in known:
        raise EngineError(f"the running engine {running!r} is not one of {known}; "
                          "state it correctly rather than letting this guess")
    for candidate in known:
        if candidate != running:
            return candidate
    raise EngineError(f"{known} leaves nothing to check {running} with")


SELFTEST = {"type": "object", "properties": {"ok": {"type": "boolean"}},
            "required": ["ok"]}


def selftest() -> int:
    """Ask each declared engine for one object. Reachability, not correctness."""
    bad = 0
    for engine in ENGINES.get("runs_on") or []:
        try:
            got = run(engine, "Reply with ok=true and nothing else.", SELFTEST)
        except EngineError as e:
            print(f"  {engine}: UNAVAILABLE — {e}")
            bad += 1
            continue
        print(f"  {engine}: answered {got}")
    known = ENGINES.get("runs_on") or []
    print(f"engines reachable: {len(known) - bad}/{len(known)} of {known}   "
          f"any of them may be the one running")
    # Unreachable is reported, never fatal: a machine without one of these still
    # runs every other check, and a hook that fails on a missing CLI gets removed.
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("engine", nargs="?", help="the checker; omit to resolve from --running")
    ap.add_argument("--running", help="the engine running this harness — required, never guessed")
    ap.add_argument("--prompt-file")
    ap.add_argument("--schema")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.running:
        print("--running is required: name the engine running this harness "
              "(it is never guessed), or pass --selftest", file=sys.stderr)
        return 2
    if not (a.prompt_file and a.schema):
        print("need --prompt-file and --schema", file=sys.stderr)
        return 2
    try:
        engine = a.engine or other_than(a.running)
        if a.running and engine == a.running:
            raise EngineError(f"{engine} is the engine running this; "
                              "a verdict from it is not a check")
        try:
            prompt = pathlib.Path(a.prompt_file).read_text(encoding="utf-8")
            schema = json.loads(pathlib.Path(a.schema).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"cannot read the prompt or schema: {e}", file=sys.stderr)
            return 2
        got = run(engine, prompt, schema)
    except EngineError as e:
        print(f"{a.engine or 'checker'}: {e}", file=sys.stderr)
        return 1
    print(json.dumps(got, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
