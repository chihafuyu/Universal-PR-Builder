"""
Script to parse and validate PR list inputs for the Universal PR Builder workflow.
"""
import json
import os
import re

raw = os.environ.get("PR_LIST", "")
parts = [part.strip() for part in raw.split(",") if part.strip()]

MAX_TARGETS = 20
pattern = re.compile(r"^(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#(?P<pr>[1-9][0-9]*)$")

if not parts:
    raise SystemExit("ERROR: pr_list must contain at least one target")

if len(parts) > MAX_TARGETS:
    raise SystemExit(f"ERROR: maximum {MAX_TARGETS} targets are allowed per run")

targets = []
seen = set()

for item in parts:
    match = pattern.fullmatch(item)
    if not match:
        raise SystemExit(f"ERROR: invalid target {item!r}; expected owner/repo#PR")

    repo = match.group("repo")
    pr = int(match.group("pr"))
    key = (repo.lower(), pr)

    if key in seen:
        raise SystemExit(f"ERROR: duplicate target: {repo}#{pr}")

    seen.add(key)
    targets.append({"repo": repo, "pr": pr})

print("targets=" + json.dumps(targets, separators=(",", ":")))
