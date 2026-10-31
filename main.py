"""
Parse and validate workflow inputs for the Universal PR Builder workflow.

Inputs (env vars):
  PR_LIST        - comma-separated gradle targets (owner/repo#PR). May be empty.
  FENNEC_VERSION - fennec versionCode (digits) or versionName (e.g. 159.0.0). May be empty.
"""
import json
import os
import re

PR_LIST = os.environ.get("PR_LIST", "").strip()
FENNEC_VERSION = os.environ.get("FENNEC_VERSION", "").strip()

if not PR_LIST and not FENNEC_VERSION:
    raise SystemExit("ERROR: at least one of pr_list or fennec_version must be provided")

MAX_TARGETS = 20
PATTERN = re.compile(r"^(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#(?P<pr>[1-9][0-9]*)$")

gradle_targets = []

if PR_LIST:
    parts = [p.strip() for p in PR_LIST.split(",") if p.strip()]
    if len(parts) > MAX_TARGETS:
        raise SystemExit(f"ERROR: maximum {MAX_TARGETS} gradle targets are allowed per run")

    seen = set()
    for item in parts:
        match = PATTERN.fullmatch(item)
        if not match:
            raise SystemExit(f"ERROR: invalid target {item!r}; expected owner/repo#PR")

        repo = match.group("repo")
        pr = int(match.group("pr"))
        key = (repo.lower(), pr)

        if key in seen:
            raise SystemExit(f"ERROR: duplicate target: {repo}#{pr}")

        if repo.lower().endswith("/fennecbuild"):
            raise SystemExit(
                f"ERROR: {repo} is not a gradle target; use the 'fennec_version' input instead"
            )

        seen.add(key)
        gradle_targets.append({"repo": repo, "pr": pr})

if FENNEC_VERSION and not re.fullmatch(r"[0-9A-Za-z._-]+", FENNEC_VERSION):
    raise SystemExit(
        f"ERROR: invalid fennec_version {FENNEC_VERSION!r}; "
        "expected versionCode (digits) or versionName (e.g. 159.0.0)"
    )

print("gradle_targets=" + json.dumps(gradle_targets, separators=(",", ":")))
print("fennec_version=" + FENNEC_VERSION)
