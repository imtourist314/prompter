#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/github_publish.sh [git_remote_url]
#
# What it does:
#   - Initializes git (if needed)
#   - Ensures the branch is main
#   - Creates an initial commit (if there are staged changes)
#   - If no remote is configured and no URL is provided, it will create the
#     GitHub repo via the GitHub CLI (gh) and set origin automatically.
#   - Optionally pushes (defaults to pushing when creating via gh)
#
# Environment variables:
#   GITHUB_REPO_NAME   Repo name to create when using gh (default: folder name)
#   GITHUB_VISIBILITY  private|public|internal (default: private)
#   GITHUB_PUSH        1 to push after setup (default: 1)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

REMOTE_URL="${1-}"
GITHUB_REPO_NAME="${GITHUB_REPO_NAME-$(basename "$ROOT_DIR")}" 
GITHUB_VISIBILITY="${GITHUB_VISIBILITY-private}"
GITHUB_PUSH="${GITHUB_PUSH-1}"

if ! command -v git >/dev/null 2>&1; then
  echo "git not found on PATH" >&2
  exit 1
fi

if [ ! -d .git ]; then
  git init
fi

# Ensure main branch
if git show-ref --quiet refs/heads/master; then
  git branch -m master main || true
fi

git checkout -B main >/dev/null

# Helpful defaults
if [ ! -f .gitignore ]; then
  cat > .gitignore <<'EOF'
node_modules/
client/node_modules/
client/dist/
.DS_Store
.env
EOF
fi

# Initial commit (or no-op)
git add -A

if git diff --cached --quiet; then
  echo "No changes staged; nothing to commit."
else
  git commit -m "Initial commit: Prompter" || true
fi

# Configure origin
if [ -n "$REMOTE_URL" ]; then
  if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "$REMOTE_URL"
  else
    git remote add origin "$REMOTE_URL"
  fi
else
  # If origin isn't set, create the repo via gh and set origin.
  if ! git remote get-url origin >/dev/null 2>&1; then
    if ! command -v gh >/dev/null 2>&1; then
      echo "No 'origin' remote is configured and GitHub CLI 'gh' was not found." >&2
      echo "Either install gh (https://cli.github.com/) or re-run with a remote URL:" >&2
      echo "  scripts/github_publish.sh <your-github-repo-url>" >&2
      exit 1
    fi

    echo "Creating GitHub repo via gh: $GITHUB_REPO_NAME ($GITHUB_VISIBILITY)"

    create_flags=(--source . --remote origin)
    case "$GITHUB_VISIBILITY" in
      public)   create_flags+=(--public) ;;
      internal) create_flags+=(--internal) ;;
      private|*) create_flags+=(--private) ;;
    esac

    if [ "$GITHUB_PUSH" = "1" ]; then
      create_flags+=(--push)
    fi

    gh repo create "$GITHUB_REPO_NAME" "${create_flags[@]}"
  fi
fi

# Push (if requested and origin exists)
if [ "$GITHUB_PUSH" = "1" ] && git remote get-url origin >/dev/null 2>&1; then
  git push -u origin main
fi

echo
echo "Done."
if git remote get-url origin >/dev/null 2>&1; then
  echo "origin: $(git remote get-url origin)"
else
  echo "origin: (not set)"
fi
