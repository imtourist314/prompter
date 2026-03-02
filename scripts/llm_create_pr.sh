#!/usr/bin/env bash
set -euo pipefail

# Creates a timestamped LLM branch, commits current working tree changes,
# generates a PR body (generated_pr.md), and opens a GitHub PR via gh.
#
# Usage:
#   scripts/llm_create_pr.sh
#
# Optional environment variables:
#   BASE_BRANCH   Base branch for PR (default: main)
#   PR_TITLE      PR title (default: "LLM enhanced changes <timestamp>")
#   COMMIT_MSG    Commit message (default: "LLM enhanced changes <timestamp>")
#   REMOTE        Git remote name (default: origin)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BASE_BRANCH="${BASE_BRANCH-main}"
REMOTE="${REMOTE-origin}"

if ! command -v git >/dev/null 2>&1; then
  echo "git not found on PATH" >&2
  exit 1
fi
if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' not found on PATH. Install from https://cli.github.com/" >&2
  exit 1
fi

# Ensure we're in a git repo
if [ ! -d .git ]; then
  echo "No .git directory found in $ROOT_DIR" >&2
  exit 1
fi

# Ensure remote exists
if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "Remote '$REMOTE' is not configured. Configure it before creating a PR." >&2
  echo "Example: git remote add $REMOTE <url>" >&2
  exit 1
fi

TS="$(date +"%Y%m%d_%H%M%S")"
BRANCH="llm_enhanced_${TS}"

PR_TITLE="${PR_TITLE-LLM enhanced changes ${TS}}"
COMMIT_MSG="${COMMIT_MSG-LLM enhanced changes ${TS}}"

# Make sure base branch exists locally
if ! git show-ref --verify --quiet "refs/heads/${BASE_BRANCH}"; then
  # try to fetch it
  git fetch "$REMOTE" "$BASE_BRANCH":"$BASE_BRANCH" >/dev/null 2>&1 || true
fi

# Start from current HEAD (assumes user already has desired changes checked out)
git checkout -b "$BRANCH" >/dev/null 2>&1 || {
  echo "Failed to create/switch to branch: $BRANCH" >&2
  exit 1
}

# Commit current changes
if git diff --quiet && git diff --cached --quiet; then
  echo "Working tree is clean; nothing to commit." >&2
  exit 1
fi

git add -A
if git diff --cached --quiet; then
  echo "No changes staged; nothing to commit." >&2
  exit 1
fi

git commit -m "$COMMIT_MSG" >/dev/null

# Push branch
git push -u "$REMOTE" "$BRANCH"

# Generate PR body
PR_BODY_FILE="generated_pr.md"
BASE_REF="${REMOTE}/${BASE_BRANCH}"

git fetch "$REMOTE" "$BASE_BRANCH" >/dev/null 2>&1 || true

{
  echo "# ${PR_TITLE}"
  echo
  echo "## Summary"
  echo "- Automated PR generated from local changes."
  echo
  echo "## Changes"
  echo "\`\`\`"
  # diffstat vs base branch if available; otherwise fall back to last commit
  if git show-ref --verify --quiet "refs/remotes/${BASE_REF}"; then
    git diff --stat "${BASE_REF}...HEAD" || true
  else
    git show --stat --oneline -1 || true
  fi
  echo "\`\`\`"
  echo
  echo "## Files changed"
  echo "\`\`\`"
  if git show-ref --verify --quiet "refs/remotes/${BASE_REF}"; then
    git diff --name-only "${BASE_REF}...HEAD" || true
  else
    git show --name-only --pretty=format: -1 || true
  fi
  echo "\`\`\`"
  echo
  echo "## Testing"
  echo "- Not specified."
} > "$PR_BODY_FILE"

# Create PR
PR_URL="$(gh pr create --base "$BASE_BRANCH" --head "$BRANCH" --title "$PR_TITLE" --body-file "$PR_BODY_FILE")"

echo
echo "PR created: $PR_URL"
