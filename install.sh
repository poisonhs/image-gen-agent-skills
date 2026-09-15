#!/usr/bin/env bash
#
# image-gen-agent-skills — universal installer
#
# Installs the bundled Agent Skills (SKILL.md open standard, agentskills.io)
# into one or more AI coding agent toolchains. Pure bash + coreutils.
#
# Usage:
#   ./install.sh                          # auto-detect installed agents, install to each
#   ./install.sh --all                    # install to every known global location
#   ./install.sh --agent claude,gemini    # install to specific agents
#   ./install.sh --project /path/to/repo  # repo-local (.agents/skills, .claude/skills, ...)
#   ./install.sh --path ~/my/skills       # custom target directory
#   ./install.sh --list                   # show known agents and resolved paths
#   ./install.sh --dry-run                # print actions without writing
#   ./install.sh --uninstall              # remove these skills from the targets
#
set -euo pipefail

SKILLS=(z-image-generation asian-adult-image-prompts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/skills"

GLOBAL_AGENTS="agents claude codex opencode cursor gemini copilot cline hermes vibe"
PROJECT_AGENTS="agents claude codex opencode cursor gemini copilot cline windsurf"

# ---------------------------------------------------------------- target paths
global_dir() {
  case "$1" in
    agents)   printf '%s\n' "$HOME/.agents/skills" ;;
    claude)   printf '%s\n' "$HOME/.claude/skills" ;;
    codex)    printf '%s\n' "$HOME/.codex/skills" ;;
    opencode) printf '%s\n' "$HOME/.config/opencode/skills" ;;
    cursor)   printf '%s\n' "$HOME/.cursor/skills" ;;
    gemini)   printf '%s\n' "$HOME/.gemini/skills" ;;
    copilot)  printf '%s\n' "$HOME/.copilot/skills" ;;
    cline)    printf '%s\n' "$HOME/.cline/skills" ;;
    hermes)   printf '%s\n' "$HOME/.hermes/skills" ;;
    vibe)     printf '%s\n' "$HOME/.vibe/skills" ;;
    *) return 1 ;;
  esac
}

project_dir() {
  local root="$1"
  case "$2" in
    agents)   printf '%s\n' "$root/.agents/skills" ;;
    claude)   printf '%s\n' "$root/.claude/skills" ;;
    codex)    printf '%s\n' "$root/.agents/skills" ;;
    opencode) printf '%s\n' "$root/.opencode/skills" ;;
    cursor)   printf '%s\n' "$root/.cursor/skills" ;;
    gemini)   printf '%s\n' "$root/.gemini/skills" ;;
    copilot)  printf '%s\n' "$root/.github/skills" ;;
    cline)    printf '%s\n' "$root/.cline/skills" ;;
    windsurf) printf '%s\n' "$root/.windsurf/skills" ;;
    *) return 1 ;;
  esac
}

config_dir() {   # where an agent keeps its config, used for auto-detection
  case "$1" in
    agents)   printf '%s\n' "$HOME/.agents" ;;
    claude)   printf '%s\n' "$HOME/.claude" ;;
    codex)    printf '%s\n' "$HOME/.codex" ;;
    opencode) printf '%s\n' "$HOME/.config/opencode" ;;
    cursor)   printf '%s\n' "$HOME/.cursor" ;;
    gemini)   printf '%s\n' "$HOME/.gemini" ;;
    copilot)  printf '%s\n' "$HOME/.copilot" ;;
    cline)    printf '%s\n' "$HOME/.cline" ;;
    hermes)   printf '%s\n' "$HOME/.hermes" ;;
    vibe)     printf '%s\n' "$HOME/.vibe" ;;
    *) return 1 ;;
  esac
}

usage() { sed -n '3,20p' "$0" | sed 's/^# \{0,1\}//'; }

# ------------------------------------------------------------------- arg parse
MODE="install"
AGENTS=""
PROJECT_ROOT=""
CUSTOM_PATH=""
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --all)         AGENTS="$GLOBAL_AGENTS" ;;
    --agent)       AGENTS="${2:?--agent needs a value}"; shift ;;
    --agent=*)     AGENTS="${1#*=}" ;;
    --project)     PROJECT_ROOT="${2:?--project needs a path}"; shift ;;
    --project=*)   PROJECT_ROOT="${1#*=}" ;;
    --path)        CUSTOM_PATH="${2:?--path needs a value}"; shift ;;
    --path=*)      CUSTOM_PATH="${1#*=}" ;;
    --list)        MODE="list" ;;
    --dry-run)     DRY_RUN=1 ;;
    --uninstall)   MODE="uninstall" ;;
    -h|--help)     usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

# ------------------------------------------------------------- resolve targets
TARGETS=()

if [ -n "$CUSTOM_PATH" ]; then
  TARGETS+=("$CUSTOM_PATH")
fi

if [ -n "$AGENTS" ]; then
  IFS=',' read -r -a wanted <<< "$AGENTS"
  for a in "${wanted[@]}"; do
    a="$(printf '%s' "$a" | tr '[:upper:]' '[:lower:]' | tr -d ' ')"
    [ -z "$a" ] && continue
    if [ -n "$PROJECT_ROOT" ]; then
      p="$(project_dir "$PROJECT_ROOT" "$a")" || { echo "unknown agent: $a" >&2; exit 2; }
    else
      p="$(global_dir "$a")" || { echo "unknown agent: $a" >&2; exit 2; }
    fi
    TARGETS+=("$p")
  done
fi

if [ "${#TARGETS[@]}" -eq 0 ] && [ "$MODE" != "list" ]; then
  # auto-detect
  detected=0
  for a in $GLOBAL_AGENTS; do
    d="$(config_dir "$a")"
    if [ -d "$d" ]; then
      if [ -n "$PROJECT_ROOT" ]; then
        TARGETS+=("$(project_dir "$PROJECT_ROOT" "$a")")
      else
        TARGETS+=("$(global_dir "$a")")
      fi
      detected=1
    fi
  done
  if [ "$detected" -eq 0 ]; then
    if [ -n "$PROJECT_ROOT" ]; then
      TARGETS+=("$(project_dir "$PROJECT_ROOT" agents)")
      echo "[i] no agent config detected — using universal repo path" >&2
    else
      TARGETS+=("$(global_dir agents)")
      echo "[i] no agent config detected — using universal path ~/.agents/skills" >&2
    fi
  fi
fi

if [ "${#TARGETS[@]}" -eq 0 ] && [ "$MODE" != "list" ]; then
  echo "no install targets resolved" >&2
  exit 1
fi

# dedupe targets while preserving order
UNIQ=()
for t in "${TARGETS[@]}"; do
  dup=0
  for u in "${UNIQ[@]:-}"; do [ "$u" = "$t" ] && dup=1 && break; done
  [ "$dup" -eq 0 ] && UNIQ+=("$t")
done
TARGETS=("${UNIQ[@]}")

# ------------------------------------------------------------------- --list
if [ "$MODE" = "list" ]; then
  echo "Supported agents (global scope):"
  for a in $GLOBAL_AGENTS; do printf '  %-9s %s\n' "$a" "$(global_dir "$a")"; done
  echo
  echo "Supported agents (project scope, --project DIR):"
  for a in $PROJECT_AGENTS; do printf '  %-9s %s\n' "$a" "$(project_dir '<DIR>' "$a")"; done
  echo
  echo "Bundled skills: ${SKILLS[*]}"
  exit 0
fi

# ---------------------------------------------------------------- sanity check
for s in "${SKILLS[@]}"; do
  if [ ! -f "$SRC_DIR/$s/SKILL.md" ]; then
    echo "missing skill source: $SRC_DIR/$s/SKILL.md" >&2
    exit 1
  fi
done

# ------------------------------------------------------------------- execute
run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

for t in "${TARGETS[@]}"; do
  case "$MODE" in
    install)
      echo "[+] $t"
      run mkdir -p "$t"
      for s in "${SKILLS[@]}"; do
        run rm -rf "${t:?}/$s"
        run cp -R "$SRC_DIR/$s" "$t/$s"
        echo "      installed $s"
      done
      ;;
    uninstall)
      echo "[-] $t"
      for s in "${SKILLS[@]}"; do
        if [ -e "$t/$s" ]; then
          run rm -rf "${t:?}/$s"
          echo "      removed $s"
        fi
      done
      ;;
  esac
done

if [ "$MODE" = "install" ]; then
  echo
  echo "Done. Skills: ${SKILLS[*]}"
  echo "Restart your agent session so it rescans the skills directory."
fi
