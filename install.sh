#!/usr/bin/env bash
set -euo pipefail

# Physical paths throughout (`pwd -P`, which macOS's bash 3.2 and BSD tools have,
# unlike `readlink -f`). A logical path made a run through a symlinked checkout
# and a run through the real one refuse each other's links; the Makefile
# resolves the same way.
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SRC_DIR="$REPO_DIR/skills"
DEST_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
MODE="link"

FORCE=0

usage() {
  cat <<'USAGE'
Usage: ./install.sh [--copy] [--uninstall] [--dest DIR] [--force]

  (default)     symlink skills/operation-* into ~/.claude/skills/
  --copy        copy instead of symlinking (does not track updates; tools stay
                linked into this repo, which must remain in place)
  --uninstall   remove the operation-* skills THIS repo installed
  --dest DIR    install into DIR instead of ~/.claude/skills
  --force       overwrite a target that is not a symlink into this repo

By default this script refuses to touch anything at the target path that it did not
install — a real directory, or a symlink pointing somewhere else. Those are your files.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy)      MODE="copy";      shift ;;
    --uninstall) MODE="uninstall"; shift ;;
    --dest)
      [[ $# -ge 2 && -n "$2" && "$2" != -* ]] || { echo "--dest needs a directory" >&2; usage; exit 1; }
      DEST_DIR="$2"; shift 2 ;;
    --force)     FORCE=1;          shift ;;
    -h|--help)   usage; exit 0 ;;
    *)           echo "unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

# A --copy install leaves this file behind, naming the source it came from, so a
# later --copy or --uninstall can tell its own copy from a directory you made.
STAMP=".installed-from"

# Is $1 something this repo installed? A symlink resolving inside $SRC_DIR, or a
# copy stamped with $SRC_DIR.
ours() {
  local target="$1" link resolved
  if [[ -L "$target" ]]; then
    # Read the link before changing directory: with a relative --dest, the
    # target's own path means nothing once the subshell has cd'd beside it.
    link="$(readlink "$target")"
    resolved="$(cd "$(dirname "$target")" && cd "$link" 2>/dev/null && pwd -P)" || return 1
    [[ "$resolved" == "$SRC_DIR"/* ]]
  else
    [[ -f "$target/$STAMP" && "$(cat "$target/$STAMP")" == "$SRC_DIR" ]]
  fi
}

refuse() {
  echo "refusing $1 — not installed by this repo." >&2
  echo "  It is $(if [[ -L $1 ]]; then echo "a symlink to $(readlink "$1")"; else echo "a real directory"; fi)." >&2
  echo "  Move it aside, or re-run with --force to overwrite it." >&2
  SKIPPED=$((SKIPPED + 1))
}

SKIPPED=0

# Uninstalling from a directory that is not there is a no-op, not a reason to make one.
if [[ "$MODE" == "uninstall" ]]; then
  [[ -d "$DEST_DIR" ]] || { echo "nothing to remove — $DEST_DIR does not exist"; exit 0; }
else
  mkdir -p "$DEST_DIR"
fi

for src in "$SRC_DIR"/operation-*; do
  [[ -d "$src" ]] || continue
  # A skill is a directory holding a SKILL.md, as `make link` reads it; the
  # prefix alone is not the test. Uninstall still looks at every prefixed name,
  # and removes only what ours() recognises.
  [[ "$MODE" == "uninstall" || -f "$src/SKILL.md" ]] || continue
  name="$(basename "$src")"
  dest="$DEST_DIR/$name"

  case "$MODE" in
    uninstall)
      if [[ -e "$dest" || -L "$dest" ]]; then
        if ours "$dest" || [[ $FORCE -eq 1 ]]; then
          rm -rf "$dest"
          echo "removed  $dest"
        else
          refuse "$dest"
        fi
      fi
      ;;
    copy)
      if [[ -e "$dest" || -L "$dest" ]] && ! ours "$dest" && [[ $FORCE -eq 0 ]]; then
        refuse "$dest"; continue
      fi
      rm -rf "$dest"
      # resolve the _operation symlink so the copy is self-contained
      cp -RL "$src" "$dest"
      # A tool is not self-contained: refute.py imports engine.py beside it and
      # reads the registry two levels up, so a dereferenced copy cannot start.
      # Tools stay links into this repo, which a copy install still needs.
      for tool in "$src"/*.py; do
        [[ -L "$tool" ]] || continue
        tool_dir="$(cd "$(dirname "$tool")" && cd "$(dirname "$(readlink "$tool")")" && pwd -P)"
        rm -f "$dest/$(basename "$tool")"
        ln -s "$tool_dir/$(basename "$(readlink "$tool")")" "$dest/$(basename "$tool")"
      done
      printf '%s\n' "$SRC_DIR" > "$dest/$STAMP"
      echo "copied   $dest"
      ;;
    link)
      if [[ -e "$dest" || -L "$dest" ]] && ! ours "$dest" && [[ $FORCE -eq 0 ]]; then
        refuse "$dest"; continue
      fi
      rm -rf "$dest"
      ln -s "$src" "$dest"
      echo "linked   $dest -> $src"
      ;;
  esac
done

if [[ $SKIPPED -gt 0 ]]; then
  echo
  echo "$SKIPPED skill(s) skipped — see the messages above." >&2
fi

if [[ "$MODE" != "uninstall" ]]; then
  echo
  echo "Installed into $DEST_DIR. Restart Claude Code to pick up the new skills."
fi
