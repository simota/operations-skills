# Wire this repo into a skills directory, and keep it inside its budgets.
#
# The repo is the single source of truth: each operation-* directory is symlinked
# individually into every installed CLI's skills directory (claude, codex,
# agy), so each of those directories keeps whatever else it already carries.

# The physical path: install.sh resolves the same way, so a link either one made
# through a symlinked checkout is recognised by the other.
REPO       := $(shell pwd -P)
CLAUDE_DIR ?= $(HOME)/.claude/skills
CODEX_DIR  ?= $(HOME)/.codex/skills
AGY_DIR    ?= $(HOME)/.gemini/antigravity-cli/skills

# Every CLI reading a SKILL.md gets the same working tree. A host is only
# written to when it is installed here, and its own home — the parent of the
# skills directory — is what says so: judging by the skills directory itself
# would skip a host that has one but has never been given a skill.
HOST_DIRS  := $(CLAUDE_DIR) $(CODEX_DIR) $(AGY_DIR)

.DEFAULT_GOAL := help
.PHONY: help check validate test figures engines refute render hooks link unlink status

help:
	@echo "make check     validate + test + figures (what CI runs)"
	@echo "make validate  static rules over the corpus"
	@echo "make test      prove every rule still fires"
	@echo "make figures   re-check the ansible / aws / gcloud claims against the installed CLIs"
	@echo "make refute CLAIMS=f.json RUNNING=claude   put each claim to the engines that did not make it"
	@echo "make engines   ask each checker engine for one object; reports what is unreachable"
	@echo "make render    write the delivered blocks back into every SKILL.md"
	@echo "make hooks     install the pre-commit hook"
	@echo "make link      symlink the skills into claude / codex / agy"
	@echo "make unlink    remove those symlinks"
	@echo "make status    show what is linked"

check: validate test figures

validate:
	@python3 operation-tools/validate.py

test:
	@python3 operation-tools/test_validate.py

figures:
	@python3 operation-tools/figures_check.py

engines:
	@python3 operation-tools/engine.py --selftest

refute:
	@test -n "$(CLAIMS)" || { echo "usage: make refute CLAIMS=claims.json RUNNING=claude"; exit 2; }
	@python3 operation-tools/refute.py --running "$(or $(RUNNING),claude)" "$(CLAIMS)"

render:
	@python3 operation-tools/render.py

# Wherever git looks for hooks: a worktree's .git is a file, and core.hooksPath
# moves them. Linked, not copied, so a change to the hook reaches every clone.
# A pre-commit hook that is not this repo's belongs to someone else — another
# tool's, or the reader's own — and is left alone, as link and unlink leave
# foreign skills alone: replacing it would silently drop whatever it checked.
# This repo's is a link into one of its own worktrees' githooks/pre-commit — a
# linked worktree shares the hooks directory with a checkout at another path,
# and may carry a different hook — or a copy of this one. A live link is left
# where it points, so a worktree never moves the shared hook onto itself; a
# dangling one with this layout (its checkout moved or removed) runs nothing and
# is repaired. A link into another project with the same layout, or a dangling
# link of any other shape (a hook manager's target gone for now), is foreign. core.hooksPath may
# point at operation-tools/githooks itself, which must never be linked onto itself.
hooks:
	@d="$$(git rev-parse --git-path hooks)" && mkdir -p "$$d" && \
		src="$(REPO)/operation-tools/githooks/pre-commit" && t="$$d/pre-commit" && \
		chmod +x "$$src" && \
		if [ "$$t" -ef "$$src" ]; then echo "pre-commit installed in $$d"; exit 0; fi && \
		ours= && if [ -L "$$t" ]; then lt="$$(readlink "$$t")"; \
			case "$$lt" in */operation-tools/githooks/pre-commit) \
				if [ ! -e "$$t" ]; then ours=1; else \
				p="$$(cd "$$(dirname "$$t")" && cd "$$(dirname "$$lt")/../.." && pwd -P)"; \
				if git worktree list --porcelain | sed -n 's/^worktree //p' | grep -Fxq "$$p"; \
				then ours=1; fi; fi ;; esac; fi && \
		if [ -n "$$ours" ] && [ -e "$$t" ]; then chmod +x "$$t" || exit 1; \
			echo "pre-commit installed in $$d (from $$(readlink "$$t"))"; exit 0; fi && \
		if [ -z "$$ours" ] && { [ -e "$$t" ] || [ -L "$$t" ]; } && ! cmp -s "$$t" "$$src"; then \
			echo "pre-commit not installed: $$t is already there and is not this repo's hook;"; \
			echo "  remove it, or call $$src from it"; exit 1; fi && \
		ln -sf "$$src" "$$t" && \
		echo "pre-commit installed in $$d"

# A link is ours only when it resolves into this repository's skills/. Anything
# else at the target — a real directory, or a symlink into another set — belongs
# to someone else and is left alone by both link and unlink, as install.sh does.
# Resolved physically, so a link made through a symlinked checkout still counts;
# a dangling link falls back to its literal text.
OURS = { r="$$(cd "$$target" 2>/dev/null && pwd -P)" || r="$$(readlink "$$target")"; \
	case "$$r" in "$(REPO)/skills/"*) true ;; *) false ;; esac; }

# A skill is a directory holding a SKILL.md, under skills/ where the plugin
# format expects it. The prefix alone is not the test: operation-registry/ and
# operation-tools/ share it and must never be installed.
SKILL_DIRS := $(patsubst %/SKILL.md,%,$(wildcard skills/operation-*/SKILL.md))

link:
	@for dir in $(HOST_DIRS); do \
		if [ ! -d "$$(dirname "$$dir")" ]; then echo "skip $$dir (host not installed here)"; continue; fi; \
		mkdir -p "$$dir"; \
		echo "$$dir"; \
		for path in $(SKILL_DIRS); do \
			name=$$(basename "$$path"); target="$$dir/$$name"; \
			if [ -e "$$target" ] && [ ! -L "$$target" ]; then \
				echo "  skip $$name (a real path is already there)"; \
			elif [ -L "$$target" ] && ! $(OURS); then \
				echo "  skip $$name (a symlink into $$(readlink "$$target") is already there)"; \
			else \
				ln -sfn "$(REPO)/$$path" "$$target"; echo "  link $$name"; \
			fi; \
		done; \
	done

unlink:
	@for dir in $(HOST_DIRS); do \
		[ -d "$$dir" ] || continue; \
		echo "$$dir"; \
		for path in $(SKILL_DIRS); do \
			name=$$(basename "$$path"); target="$$dir/$$name"; \
			if [ -L "$$target" ] && $(OURS); then rm "$$target"; echo "  unlink $$name"; \
			elif [ -L "$$target" ]; then echo "  skip $$name (not linked by this repo)"; fi; \
		done; \
	done

status:
	@for dir in $(HOST_DIRS); do \
		echo "$$dir"; \
		for path in $(SKILL_DIRS); do \
			name=$$(basename "$$path"); target="$$dir/$$name"; \
			if [ -L "$$target" ] && $(OURS); then echo "  linked   $$name"; \
			elif [ -e "$$target" ] || [ -L "$$target" ]; then echo "  foreign  $$name"; \
			else echo "  unlinked $$name"; fi; \
		done; \
	done
