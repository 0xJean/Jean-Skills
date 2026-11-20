#!/usr/bin/env bash
# Idempotently create or update standard GitHub team workflow labels via gh CLI.
# Usage: ./init-labels.sh [owner/repo]

set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh CLI is required. Install from https://cli.github.com/" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Error: gh CLI is not authenticated. Run 'gh auth login' first." >&2
  exit 1
fi

REPO_FLAG=()
if [ "${1:-}" != "" ]; then
  REPO_FLAG=(--repo "$1")
fi

upsert_label() {
  local name="$1"
  local color="$2"
  local description="$3"
  # Use ${REPO_FLAG[@]+...} so Bash 3.2 (default on macOS) does not fail with
  # "unbound variable" under `set -u` when REPO_FLAG is empty.
  gh label create "$name" --color "$color" --description "$description" --force ${REPO_FLAG[@]+"${REPO_FLAG[@]}"}
}

# Type labels
upsert_label "type:bug" "d73a4a" "Defect or unexpected behavior"
upsert_label "type:feature" "0e8a16" "Repository-scoped feature task"
upsert_label "type:hotfix" "b60205" "Production incident requiring urgent hotfix"

# Priority labels
upsert_label "priority:p0" "b60205" "Critical outage or data risk; immediate hotfix"
upsert_label "priority:p1" "d93f0b" "High priority; required in current cycle"
upsert_label "priority:p2" "fbca04" "Normal priority; scheduled in backlog"
upsert_label "priority:p3" "c5def5" "Low priority optimization; deferrable"

# Status and workflow labels
upsert_label "needs-info" "d876e3" "Waiting for reproduction steps or clarification"
upsert_label "blocked" "e99695" "Blocked by an external or cross-repo dependency"
upsert_label "qa-approved" "0e8a16" "Verified on staging and signed off by QA"

# Resolution and onboarding labels
upsert_label "duplicate" "cfd3d7" "Duplicate of an existing Issue"
upsert_label "wontfix" "ffffff" "Out of scope or will not be addressed"
upsert_label "good first issue" "7057ff" "Well-scoped task suitable for newcomers"

# Add repository-specific area:* labels matching CODEOWNERS as needed, for example:
# upsert_label "area:frontend" "1d76db" "Frontend modules"
# upsert_label "area:backend" "0052cc" "Backend services"

echo "Standard workflow labels synced successfully."
