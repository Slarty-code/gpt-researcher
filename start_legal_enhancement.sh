#!/bin/bash

# Legal Enhancement Startup Script
# This script starts the legal enhancement API server with proper error handling

echo "🚀 Starting Legal Document Enhancement API Server..."
echo "=================================================="

# Check if required environment variables are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set. Some features may not work."
fi

# Wait for GPT Researcher to be ready (optional)
echo "⏳ Waiting for GPT Researcher to be ready..."
if [ ! -z "$GPT_RESEARCHER_URL" ]; then
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s "$GPT_RESEARCHER_URL" > /dev/null 2>&1; then
            echo "✅ GPT Researcher is ready!"
            break
        fi
        echo "⏳ Waiting for GPT Researcher... ($timeout seconds remaining)"
        sleep 5
        timeout=$((timeout - 5))
    done
fi

# Test the legal enhancement module
echo "🧪 Testing Legal Enhancement Module..."
python -c "
import sys
sys.path.append('/app')
try:
    from legal_document_enhancement.integration import LegalDocumentEnhancement
    enhancement = LegalDocumentEnhancement()
    info = enhancement.get_processing_info()
    print(f'✅ Legal Enhancement loaded successfully!')
    print(f'   Enhanced Processing: {info[\"enhanced_processing\"]}')
    print(f'   Semantic Chunking: {info[\"semantic_chunking\"]}')
    print(f'   Document Processor: {info[\"document_processor_available\"]}')
    print(f'   Chunker: {info[\"chunker_available\"]}')
except Exception as e:
    print(f'⚠️  Legal Enhancement module test failed: {e}')
    print('   Continuing with fallback mode...')
"

# Start the API server
echo "🌐 Starting Legal Enhancement API Server on port 8001..."
echo "   API Documentation: http://localhost:8001/docs"
echo "   Health Check: http://localhost:8001/health"
echo "   GPT Researcher: $GPT_RESEARCHER_URL"
echo "=================================================="

# Start the server with proper error handling
exec python legal_api_server.py