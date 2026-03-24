# ADD CODE HERE
# change script to whatever language you are comfortable with
#!/usr/bin/env python3
"""
Terraform Plan Validator
========================
Reads a Terraform plan JSON file and decides whether `terraform apply` should
proceed, based on the following rules:

  1. Every resource change must be a `create` or `update` (modify).
  2. `no-op` changes are silently ignored (nothing is being done).
  3. Any `delete` or other destructive action → BLOCK the apply.
  4. For `update` changes, the ONLY attribute allowed to differ between
     `before` and `after` is `tags`, and within `tags` the ONLY key
     allowed to change is `GitCommitHash`.
     Any other attribute change → BLOCK the apply.

Usage
-----
    python3 script.py <tfplan.json> [<tfplan2.json> ...]

Exit codes
----------
    0  – all supplied plans are safe to apply
    1  – at least one plan was blocked

Examples
--------
    python3 script.py tfplan-1.json
    python3 script.py tfplan-1.json tfplan-2.json tfplan-3.json
"""

import json
import sys

# ──────────────────────────────────────────────────────────────────────────────
# Core validation helpers
# ──────────────────────────────────────────────────────────────────────────────

ALLOWED_ACTIONS  = {"create", "update", "no-op"}
ALLOWED_TAG_KEYS = {"GitCommitHash"}


def changed_keys(before: dict, after: dict) -> set:
    """Return the set of top-level keys whose values differ between before/after."""
    all_keys = set(before.keys()) | set(after.keys())
    return {k for k in all_keys if before.get(k) != after.get(k)}


def validate_update(resource: dict) -> list:
    """
    Validate a single `update` resource change.

    Returns a (possibly empty) list of human-readable violation strings.
    An empty list means the update is fully allowed.
    """
    address = resource.get("address", "<unknown>")
    change  = resource["change"]
    before  = change.get("before") or {}
    after   = change.get("after")  or {}

    violations = []

    for key in changed_keys(before, after):
        if key != "tags":
            violations.append(
                f"  ✗  [{address}]  non-tag attribute modified: '{key}'"
            )
            continue

        # key == "tags" 
        b_tags = before.get("tags") or {}
        a_tags = after.get("tags")  or {}

        disallowed = changed_keys(b_tags, a_tags) - ALLOWED_TAG_KEYS
        for bad_tag in sorted(disallowed):
            violations.append(
                f"  ✗  [{address}]  disallowed tag key modified: '{bad_tag}'"
            )

    return violations


def validate_plan(plan_path: str) -> bool:
    """
    Load and validate the plan at *plan_path*.

    Prints a per-resource summary and a final PASS / BLOCK verdict.
    Returns True if the apply should proceed, False if it must be blocked.
    """
    bar = "─" * 64
    print(f"\n{bar}")
    print(f"  Plan file : {plan_path}")
    print(bar)

    # ── load ──────────────────────────────────────────────────────────────────
    try:
        with open(plan_path) as fh:
            plan = json.load(fh)
    except FileNotFoundError:
        print(f"  ERROR: file not found.\n")
        return False
    except json.JSONDecodeError as exc:
        print(f"  ERROR: invalid JSON – {exc}\n")
        return False

    resource_changes = plan.get("resource_changes", [])

    if not resource_changes:
        print("  (no resource changes – nothing to apply)")
        print(f"\n  VERDICT: SAFE TO APPLY\n")
        return True

    # ── inspect every resource change ─────────────────────────────────────────
    all_violations = []

    for resource in resource_changes:
        address = resource.get("address", "<unknown>")
        actions = resource["change"].get("actions", [])

        # ── no-op: skip silently ──────────────────────────────────────────────
        if actions == ["no-op"]:
            continue

        # ── disallowed actions (delete, replace, …) ───────────────────────────
        bad_actions = [a for a in actions if a not in ALLOWED_ACTIONS]
        if bad_actions:
            all_violations.append(
                f"  ✗  [{address}]  disallowed action(s): {bad_actions}"
            )
            continue

        # ── create: always allowed ────────────────────────────────────────────
        if actions == ["create"]:
            print(f"CREATE  {address}")
            continue

        # ── update: validate what actually changed ────────────────────────────
        if "update" in actions:
            violations = validate_update(resource)
            if violations:
                all_violations.extend(violations)
                print(f"UPDATE  {address}  (disallowed changes – see below)")
            else:
                print(f"UPDATE  {address}  (GitCommitHash tag only)")
            continue

        # ── unexpected action combo ───────────────────────────────────────────
        all_violations.append(
            f"  ✗  [{address}]  unexpected action combination: {actions}"
        )

    # ── verdict ───────────────────────────────────────────────────────────────
    print()
    if all_violations:
        print("  VERDICT: BLOCKED – apply must NOT proceed.\n")
        print("  Reasons:")
        for v in all_violations:
            print(v)
        print()
        return False

    print("  VERDICT: SAFE TO APPLY\n")
    return True


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    results = [validate_plan(path) for path in sys.argv[1:]]
    sys.exit(0 if all(results) else 1)