#!/bin/bash
# Script to push to both GitHub and git.soma at once

echo "🚀 Pushing to GitHub (origin)..."
git push origin main

echo ""
echo "🚀 Pushing to git.soma (soma)..."
git push soma main

echo ""
echo "✅ Successfully pushed to both remotes!"
echo "   📦 GitHub:   https://github.com/rinkusonisalesforce/mce-prom-dashboard"
echo "   📦 git.soma: https://git.soma.salesforce.com/rinku-soni/mce-prom-dashboard"
