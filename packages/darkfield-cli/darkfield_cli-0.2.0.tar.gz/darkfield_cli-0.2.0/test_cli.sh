#!/bin/bash

echo "🧪 Testing darkfield CLI..."
echo ""

# Set to use local development server
export DARKFIELD_ENV=development

# Test 1: Show version
echo "1. Testing version:"
darkfield --version
echo ""

# Test 2: Show help
echo "2. Testing help:"
darkfield --help | head -10
echo ""

# Test 3: Show status (not authenticated)
echo "3. Testing status (not authenticated):"
darkfield status
echo ""

# Test 4: Show pricing
echo "4. Testing pricing:"
darkfield pricing
echo ""

# Test 5: Test analyze command help
echo "5. Testing analyze command help:"
darkfield analyze --help | head -10
echo ""

# Test 6: Demo mode (won't work without server)
echo "6. Testing demo (will fail without API):"
darkfield analyze demo --trait sycophancy --model llama-3 2>&1 | head -5 || true
echo ""

echo "✅ Basic CLI tests complete!"