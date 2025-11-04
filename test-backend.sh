#!/bin/bash

echo "🧪 TESTING CURALINK BACKEND ENDPOINTS"
echo "====================================="

BACKEND_URL="https://curalink-backend-7ctdu4mds-karthik24751s-projects.vercel.app"

echo "📊 Testing Trials..."
TRIALS=$(curl -s "${BACKEND_URL}/api/trials/search" | jq '.data | length' 2>/dev/null || echo "ERROR")
echo "   Clinical Trials: $TRIALS"

echo "📚 Testing Publications..."
PUBS=$(curl -s "${BACKEND_URL}/api/publications/search" | jq '.data | length' 2>/dev/null || echo "ERROR")
echo "   Publications: $PUBS"

echo "👨‍⚕️ Testing Experts..."
EXPERTS=$(curl -s "${BACKEND_URL}/api/experts/search" | jq '.data | length' 2>/dev/null || echo "ERROR")
echo "   Experts: $EXPERTS"

echo "💬 Testing Forums..."
FORUMS=$(curl -s "${BACKEND_URL}/api/forums/" | jq '.data | length' 2>/dev/null || echo "ERROR")
echo "   Forums: $FORUMS"

echo "🤖 Testing CuraAI..."
CHAT=$(curl -s "${BACKEND_URL}/api/chat/ai-assistant" \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}' | jq -r '.response' 2>/dev/null | cut -c1-30 || echo "ERROR")
echo "   CuraAI: $CHAT..."

echo ""
echo "✅ ALL ENDPOINTS SHOULD SHOW NUMBERS ABOVE 0"
echo "🔗 Backend URL: $BACKEND_URL"
