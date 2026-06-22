#!/bin/bash

echo "🔄 Updating MCE Dashboard Data..."
echo "=================================="
echo ""

# Check Python script exists
if [ ! -f "generateMCEData.py" ]; then
    echo "❌ generateMCEData.py not found"
    exit 1
fi

# Check CSV files exist
DATA_DIR="/Users/rinku.soni/prom-signature-extension/data"

echo "Checking CSV files in: $DATA_DIR"
echo ""

if [ ! -d "$DATA_DIR" ]; then
    echo "❌ Data directory not found: $DATA_DIR"
    exit 1
fi

NA_FILES=$(ls "$DATA_DIR"/NA_*.csv 2>/dev/null | wc -l)
EU_FILES=$(ls "$DATA_DIR"/EU_*.csv 2>/dev/null | wc -l)
CONTRACT_FILES=$(ls "$DATA_DIR"/contracts.csv 2>/dev/null | wc -l)

if [ "$NA_FILES" -eq 0 ]; then
    echo "❌ No NA CSV files found"
    echo "   Expected: $DATA_DIR/NA_*.csv"
    exit 1
fi

if [ "$EU_FILES" -eq 0 ]; then
    echo "❌ No EU CSV files found"
    echo "   Expected: $DATA_DIR/EU_*.csv"
    exit 1
fi

if [ "$CONTRACT_FILES" -eq 0 ]; then
    echo "❌ No contracts CSV found"
    echo "   Expected: $DATA_DIR/contracts.csv"
    exit 1
fi

echo "✅ Found CSV files:"
ls -lh "$DATA_DIR"/*.csv
echo ""

# Generate data
echo "Generating JavaScript data..."
python3 generateMCEData.py

if [ $? -ne 0 ]; then
    echo "❌ Data generation failed"
    exit 1
fi

echo ""
echo "✅ Data generated successfully!"
echo ""
echo "📄 Output: src/data/mceRealData.js"
echo ""
echo "Next steps:"
echo "1. Test locally: npm run dev"
echo "2. Deploy: npm run deploy"
echo ""
