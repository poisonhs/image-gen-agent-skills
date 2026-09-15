#!/usr/bin/env python3
"""Validate SKILL.md files against the agentskills.io open standard.

Checks every skill directory passed on the command line (default: ./skills):

  * SKILL.md exists and starts with a YAML frontmatter block
  * `name` is present, <= 64 chars, [a-z0-9-] only, no leading/trailing hyphen
  * `description` is present, non-empty, <= 1024 chars
  * frontmatter keys stay inside the portable set
    (name, description, license, compatibility, allowed-tools, metadata)
  * directory name matches the skill `name`

Exits non-zero if any error is found. Standard library only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PORTABLE_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "allowed-tools",
    "metadata",
}
NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
MAX_NAME = 64
MAX_DESC = 1024


def split_frontmatter(text: str):
    """Return (frontmatter_lines, body) or (None, text) when absent."""
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    if len(lines) < 2 or lines[0].strip() != "---":
        return None, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1 :])
    return None, text


def top_level_keys(fm_lines):
    keys = []
    for line in fm_lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] not in " \t":  # only column-0 keys are top level
            m = re.match(r"^([A-Za-z0-9_.-]+)\s*:", line)
            if m:
                keys.append(m.group(1))
    return keys


def scalar(fm_lines, key):
    """Very small YAML scalar reader: handles `key: value` and quoted values."""
    pat = re.compile(rf"^{re.escape(key)}\s*:\s*(.*)$")
    for line in fm_lines:
        if line[0] in " \t":
            continue
        m = pat.match(line)
        if not m:
            continue
        val = m.group(1).strip()
        if val in ("|", ">", "|-", ">-"):
            return val  # block scalar, treat as present
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        return val
    return None


def check_skill(skill_dir: Path):
    errors, warnings = [], []
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return [f"{skill_dir}: SKILL.md not found"], warnings

    fm, body = split_frontmatter(md.read_text(encoding="utf-8"))
    if fm is None:
        return [f"{md}: no YAML frontmatter block"], warnings

    name = scalar(fm, "name")
    desc = scalar(fm, "description")

    if not name:
        errors.append(f"{md}: `name` is required")
    else:
        if len(name) > MAX_NAME:
            errors.append(f"{md}: `name` exceeds {MAX_NAME} chars ({len(name)})")
        if not NAME_RE.match(name):
            errors.append(
                f"{md}: `name` must be lowercase alphanumeric/hyphen, no leading/"
                f"trailing hyphen (got {name!r})"
            )
        if name != skill_dir.name:
            warnings.append(
                f"{md}: `name` ({name}) differs from directory name ({skill_dir.name})"
            )

    if not desc:
        errors.append(f"{md}: `description` is required")
    elif desc in ("|", ">", "|-", ">-"):
        warnings.append(f"{md}: `description` is a block scalar — check it renders")
    else:
        if len(desc) > MAX_DESC:
            errors.append(f"{md}: `description` exceeds {MAX_DESC} chars ({len(desc)})")

    for key in top_level_keys(fm):
        if key not in PORTABLE_KEYS:
            warnings.append(
                f"{md}: non-portable frontmatter key `{key}` "
                f"(portable set: {', '.join(sorted(PORTABLE_KEYS))})"
            )

    if not body.strip():
        warnings.append(f"{md}: empty body after frontmatter")

    return errors, warnings


def main(argv):
    roots = [Path(a) for a in argv[1:]] or [Path("skills")]
    skill_dirs = []
    for root in roots:
        if not root.exists():
            print(f"skip: {root} does not exist", file=sys.stderr)
            continue
        if (root / "SKILL.md").is_file():
            skill_dirs.append(root)
        else:
            skill_dirs.extend(
                sorted(p for p in root.iterdir() if (p / "SKILL.md").is_file())
            )

    if not skill_dirs:
        print("no skills found", file=sys.stderr)
        return 1

    all_errors, all_warnings = [], []
    for d in skill_dirs:
        errs, warns = check_skill(d)
        all_errors += errs
        all_warnings += warns
        status = "FAIL" if errs else "OK"
        print(f"[{status}] {d.name}")

    for w in all_warnings:
        print(f"warn: {w}")
    for e in all_errors:
        print(f"error: {e}")

    print(
        f"\n{len(skill_dirs)} skill(s) checked — "
        f"{len(all_errors)} error(s), {len(all_warnings)} warning(s)"
    )
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
