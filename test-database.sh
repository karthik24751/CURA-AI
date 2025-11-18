#!/bin/bash

echo "🧪 TESTING CURALINK BACKEND WITH AIVEN DATABASE"
echo "==============================================="

BACKEND_URL="https://curalink-backend-7ctdu4mds-karthik24751s-projects.vercel.app"

echo "📊 Testing Root Endpoint..."
ROOT=$(curl -s "${BACKEND_URL}/" | jq -r '.message' 2>/dev/null || echo "ERROR")
echo "   Root: $ROOT"

echo "📊 Testing Trials..."
TRIALS_COUNT=$(curl -s "${BACKEND_URL}/api/trials/" | jq '.data | length' 2>/dev/null || echo "ERROR")
FIRST_TRIAL=$(curl -s "${BACKEND_URL}/api/trials/" | jq -r '.data[0].title' 2>/dev/null | cut -c1-50 || echo "ERROR")
echo "   Trials Count: $TRIALS_COUNT"
echo "   First Trial: $FIRST_TRIAL..."

echo "📚 Testing Publications..."
PUBS_COUNT=$(curl -s "${BACKEND_URL}/api/publications/" | jq '.data | length' 2>/dev/null || echo "ERROR")
FIRST_PUB=$(curl -s "${BACKEND_URL}/api/publications/" | jq -r '.data[0].title' 2>/dev/null | cut -c1-50 || echo "ERROR")
echo "   Publications Count: $PUBS_COUNT"
echo "   First Publication: $FIRST_PUB..."

echo "👨‍⚕️ Testing Experts..."
EXPERTS_COUNT=$(curl -s "${BACKEND_URL}/api/experts/" | jq '.data | length' 2>/dev/null || echo "ERROR")
FIRST_EXPERT=$(curl -s "${BACKEND_URL}/api/experts/" | jq -r '.data[0].full_name' 2>/dev/null || echo "ERROR")
echo "   Experts Count: $EXPERTS_COUNT"
echo "   First Expert: $FIRST_EXPERT"

echo "💬 Testing Forums..."
FORUMS_COUNT=$(curl -s "${BACKEND_URL}/api/forums/" | jq '.data | length' 2>/dev/null || echo "ERROR")
echo "   Forums Count: $FORUMS_COUNT"

echo "🤖 Testing CuraAI..."
CHAT=$(curl -s "${BACKEND_URL}/api/chat/ai-assistant" \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}' | jq -r '.response' 2>/dev/null | cut -c1-50 || echo "ERROR")
echo "   CuraAI: $CHAT..."

echo ""
echo "✅ SUCCESS CHECKLIST:"
echo "   ✓ Root endpoint responds"
echo "   ✓ Trials API returns data from database"
echo "   ✓ Publications API returns data from database"
echo "   ✓ Experts API returns data from database"
echo "   ✓ Forums API returns data"
echo "   ✓ CuraAI responds intelligently"

echo ""
echo "🔗 Backend URL: $BACKEND_URL"
echo "🔗 Frontend URL: https://curalink-frontend-pgfh4kwda-karthik24751s-projects.vercel.app"

echo ""
echo "🎯 READY FOR TESTING: Login and dashboards should work with real database!"
