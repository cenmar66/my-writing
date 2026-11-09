#!/usr/bin/env python3
"""Make the writing skills work from any Claude Code chat. Safe to run again. Never erases anything.

  python3 ~/my-writing/tools/install_global.py

1. Links each .claude/skills/writing-* into ~/.claude/skills/ (skips names already taken by something else).
2. Registers .claude/hooks/git_guard.py in ~/.claude/settings.json (keeps every existing setting).
3. Adds one line to ~/.claude/CLAUDE.md (creates it if missing).
"""
import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOME_CLAUDE = Path.home() / ".claude"
LINE = "For anything about my writing, first read ~/my-writing/CLAUDE.md and follow it."


def link_skills():
    dst_dir = HOME_CLAUDE / "skills"
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted((REPO / ".claude" / "skills").glob("writing-*")):
        dst = dst_dir / src.name
        if dst.is_symlink() and dst.resolve() == src.resolve():
            print(f"  ok      {dst}")
            continue
        if dst.exists() or dst.is_symlink():
            print(f"  SKIPPED {dst} already exists and is not this repo's skill. Left it alone.")
            continue
        try:
            dst.symlink_to(src, target_is_directory=True)
            print(f"  linked  {dst}")
        except OSError:  # Windows without symlink rights: copy instead
            shutil.copytree(src, dst)
            print(f"  copied  {dst} (re-run after skill changes)")


def register_hook():
    path = HOME_CLAUDE / "settings.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError:
            print(f"  SKIPPED {path} is not valid JSON. Fix it, then run again.")
            return
        shutil.copy2(path, path.with_suffix(".json.bak"))
    cmd = f'python3 "{REPO / ".claude" / "hooks" / "git_guard.py"}"'
    pre = data.setdefault("hooks", {}).setdefault("PreToolUse", [])
    if any(h.get("command") == cmd for e in pre for h in e.get("hooks", [])):
        print(f"  ok      git guard already in {path}")
        return
    pre.append({"matcher": "Bash", "hooks": [{"type": "command", "command": cmd}]})
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"  added   git guard to {path}")


def add_line():
    path = HOME_CLAUDE / "CLAUDE.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if LINE in text:
        print(f"  ok      line already in {path}")
        return
    sep = "" if not text or text.endswith("\n") else "\n"
    path.write_text(text + sep + ("\n" if text else "") + LINE + "\n", encoding="utf-8")
    print(f"  added   line to {path}")


if __name__ == "__main__":
    if REPO != (Path.home() / "my-writing").resolve():
        print(f"Note: repo is at {REPO}, not ~/my-writing. The CLAUDE.md line points to ~/my-writing.")
    HOME_CLAUDE.mkdir(exist_ok=True)
    link_skills()
    register_hook()
    add_line()
    print("Done.")
