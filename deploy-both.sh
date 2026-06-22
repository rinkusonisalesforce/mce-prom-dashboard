#!/bin/bash
# Script to deploy Pages to both GitHub and git.soma

echo "🏗️  Building dashboard..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "🚀 Deploying to GitHub Pages..."
git push origin `git subtree split --prefix dist main`:gh-pages --force

echo ""
echo "🚀 Deploying to git.soma Pages..."
git push soma `git subtree split --prefix dist main`:gh-pages --force

echo ""
echo "✅ Successfully deployed to both Pages!"
echo "   🌐 GitHub Pages:   https://rinkusonisalesforce.github.io/mce-prom-dashboard/"
echo "   🌐 git.soma Pages: https://git.soma.salesforce.com/pages/rinku-soni/mce-prom-dashboard/"
