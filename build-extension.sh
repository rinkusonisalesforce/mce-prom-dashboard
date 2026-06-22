#!/bin/bash

echo "🔨 Building MCE ProM Dashboard Extension..."
echo ""

# Build the React app
echo "Step 1: Building React app..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# Copy extension-specific files
echo ""
echo "Step 2: Copying extension files..."
cp public/manifest.json dist/
cp public/jsforce.js dist/
cp -r /Users/rinku.soni/prom-signature-extension/data dist/

# Copy utility scripts
mkdir -p dist/src
cp src/utils/config.js dist/src/
cp src/utils/sf-orgs.js dist/src/
cp src/utils/core.js dist/src/
cp src/utils/csv.js dist/src/

echo ""
echo "✅ Extension built successfully!"
echo ""
echo "📦 Extension files are in: dist/"
echo ""
echo "To install:"
echo "1. Open Chrome → Extensions (chrome://extensions/)"
echo "2. Enable 'Developer mode'"
echo "3. Click 'Load unpacked'"
echo "4. Select the 'dist' folder"
echo ""
