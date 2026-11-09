#!/usr/bin/env python3
"""Blocks git commands that can erase another chat's work. Claude Code PreToolUse hook for Bash.

Blocked: git add -A / --all / . / -u, commit -a, push --force (any form), reset --hard, rebase,
clean -f, checkout . , restore . , and stash without a path.
Allowed: everything else, e.g. `git add feedback/rules.md`, `git stash push -- some/file.md`.
"""
import json
import re
import shlex
import sys

WHOLE_TREE = {".", "./", ":/", "*", "-A", "--all", "-u", "--update", ":"}


def split_commands(cmd):
    return [c for c in re.split(r"&&|\|\||;|\||\n|\$\(|`", cmd) if c.strip()]


def git_args(part):
    try:
        toks = shlex.split(part, posix=True)
    except ValueError:
        toks = part.split()
    while toks and re.match(r"^\w+=", toks[0]):  # VAR=x git ...
        toks = toks[1:]
    while toks and toks[0] in ("sudo", "command", "env", "time", "nohup"):
        toks = toks[1:]
    if not toks or not re.search(r"(^|/)git$", toks[0]):
        return None
    toks = toks[1:]
    while toks and toks[0].startswith("-"):  # global options: -C dir, -c k=v, --no-pager
        opt = toks.pop(0)
        if opt in ("-C", "-c", "--git-dir", "--work-tree") and toks:
            toks.pop(0)
    return toks


def short_flags(args):
    return {c for a in args if re.match(r"^-[A-Za-z]+$", a) for c in a[1:]}


def why_blocked(args):
    if not args:
        return None
    sub, rest = args[0], args[1:]
    flags = short_flags(rest)
    paths = rest[rest.index("--") + 1:] if "--" in rest else [a for a in rest if not a.startswith("-")]
    if sub == "add" and (WHOLE_TREE & set(rest) or "A" in flags or "u" in flags):
        return "git add of the whole tree. Add files by path: git add path/one.md path/two.md"
    if sub == "commit" and ("a" in flags or "--all" in rest):
        return "git commit -a. Stage files by path, then git commit -m ..."
    if sub == "push" and ("f" in flags or any(a.startswith("--force") for a in rest) or any(a.startswith("+") for a in rest)):
        return "force push"
    if sub == "reset" and "--hard" in rest:
        return "git reset --hard"
    if sub == "rebase":
        return "git rebase"
    if sub == "clean" and ("f" in flags or "--force" in rest):
        return "git clean -f"
    if sub in ("checkout", "restore") and (WHOLE_TREE & set(paths)):
        return f"git {sub} of the whole tree. Name the file: git {sub} -- path/file.md"
    if sub == "stash":
        action = rest[0] if rest and not rest[0].startswith("-") else "push"
        if action in ("list", "show"):
            return None
        if action == "push" and "--" in rest and paths:
            return None
        return "git stash without a path. Use: git stash push -- path/file.md"
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command", "")
    for part in split_commands(cmd):
        args = git_args(part.strip())
        reason = why_blocked(args) if args is not None else None
        if reason:
            print(f"Blocked by git_guard: {reason}. Two chats can share this repo, so only path-scoped, "
                  f"non-destructive git is allowed.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
