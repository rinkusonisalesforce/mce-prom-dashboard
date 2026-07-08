#!/bin/bash
# Script to manually (re)deploy Pages to both GitHub and git.soma.
#
# Note: GitHub Pages is normally auto-deployed by
# .github/workflows/deploy.yml whenever main is pushed — you usually don't
# need to run this for GitHub. git.soma has no CI equivalent, so its
# gh-pages branch must be deployed this way (this is also done automatically
# by weekly-update.sh's Step 7).
#
# dist/ is gitignored, so `git subtree push` finds no committed history to
# push — instead we build fresh and force-push the raw dist/ output as the
# entire content of each gh-pages branch, via a throwaway worktree.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🏗️  Building dashboard..."
npm run build

deploy_to() {
    local remote=$1
    local label=$2
    echo ""
    echo "🚀 Deploying to $label Pages..."

    local worktree
    worktree=$(mktemp -d "${TMPDIR:-/tmp}/deploy-gh-pages.XXXXXX")

    git fetch "$remote" gh-pages >/dev/null 2>&1 || true

    if git rev-parse --verify "$remote/gh-pages" >/dev/null 2>&1; then
        git worktree add --detach "$worktree" "$remote/gh-pages" >/dev/null 2>&1
    else
        git worktree add --detach "$worktree" >/dev/null 2>&1
        (cd "$worktree" && git checkout --orphan gh-pages >/dev/null 2>&1 && git rm -rf . >/dev/null 2>&1 || true)
    fi

    (
        cd "$worktree"
        git rm -rf . >/dev/null 2>&1 || true
        cp -r "$SCRIPT_DIR/dist/." "$worktree/"
        git add -A
        if git diff --staged --quiet; then
            echo "   ℹ️  $label Pages already up to date — nothing to deploy"
        else
            git commit -q -m "Auto-deploy dashboard update $(cd "$SCRIPT_DIR" && git rev-parse main)"
            git push "$remote" HEAD:gh-pages
            echo "   ✅ Deployed to $label Pages"
        fi
    )

    cd "$SCRIPT_DIR"
    git worktree remove "$worktree" --force >/dev/null 2>&1
    rm -rf "$worktree" 2>/dev/null || true
}

deploy_to origin "GitHub"
deploy_to soma "git.soma"

echo ""
echo "✅ Deploy complete!"
echo "   🌐 GitHub Pages:   https://rinkusonisalesforce.github.io/mce-prom-dashboard/"
echo "   🌐 git.soma Pages: https://git.soma.salesforce.com/pages/rinku-soni/mce-prom-dashboard/"
