#!/bin/bash
# Complete deployment script for both GitHub and git.soma Pages

set -e  # Exit on any error

echo "🏗️  Building dashboard..."
npm run build

echo ""
echo "📦 Deploying to GitHub Pages..."
npm run deploy

echo ""
echo "📦 Deploying to git.soma Pages..."
CURRENT_BRANCH=$(git branch --show-current)
git checkout gh-pages
git pull origin gh-pages
git push soma gh-pages
git checkout $CURRENT_BRANCH

echo ""
echo "✅ Successfully deployed to both Pages!"
echo "   🌐 GitHub Pages:   https://rinkusonisalesforce.github.io/mce-prom-dashboard/"
echo "   🌐 git.soma Pages: https://git.soma.salesforce.com/pages/rinku-soni/mce-prom-dashboard/"
echo ""
echo "⏳ Wait 1-2 minutes for git.soma to rebuild..."
