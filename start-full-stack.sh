#!/bin/bash
# GPT Researcher Full Stack Startup Script

set -e

echo "🚀 Starting GPT Researcher Full Stack..."
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs

# Check if environment file exists
if [ ! -f "env.full-stack" ]; then
    echo "⚠️  Environment file not found. Creating from template..."
    cp env.full-stack env.full-stack.local
    echo "📝 Please edit env.full-stack.local with your configuration"
    echo "   Especially set your OPENAI_API_KEY"
    exit 1
fi

# Load environment variables
echo "🔧 Loading environment variables..."
export $(cat env.full-stack | grep -v '^#' | xargs)

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY is not set. Please set it in env.full-stack"
    exit 1
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.full-stack.yml up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check GPT Researcher
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ GPT Researcher is healthy"
else
    echo "❌ GPT Researcher is not healthy"
fi

# Check Legal Enhancement
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Legal Enhancement is healthy"
else
    echo "❌ Legal Enhancement is not healthy"
fi

# Check OWUI Bridge
if curl -f http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ OWUI Bridge is healthy"
else
    echo "❌ OWUI Bridge is not healthy"
fi

# Check OWUI (if enabled)
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ OWUI is healthy"
else
    echo "⚠️  OWUI is not accessible (may still be starting)"
fi

echo ""
echo "🎉 GPT Researcher Full Stack is starting!"
echo "========================================"
echo "📊 Services:"
echo "   GPT Researcher:    http://localhost:8000"
echo "   Legal Enhancement: http://localhost:8001"
echo "   OWUI Bridge:       http://localhost:8002"
echo "   OWUI Frontend:     http://localhost:3000"
echo "   ChromaDB:          http://localhost:8003"
echo "   Redis:             localhost:6379"
echo ""
echo "📁 Data Directory: ./data"
echo "📝 Logs Directory: ./logs"
echo ""
echo "🔧 To stop all services:"
echo "   docker-compose -f docker-compose.full-stack.yml down"
echo ""
echo "🔧 To view logs:"
echo "   docker-compose -f docker-compose.full-stack.yml logs -f"
echo ""
echo "🔧 To restart a service:"
echo "   docker-compose -f docker-compose.full-stack.yml restart <service-name>"
echo ""
echo "🎯 Ready to process your legal corpus!"