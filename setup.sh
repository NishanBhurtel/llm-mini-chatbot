#!/bin/bash

# GitHubProfileBot Setup & Run Script

echo "🤖 GitHubProfileBot Setup"
echo "========================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7+"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the bot:"
echo "   Interactive CLI:    python3 github_profile_bot.py"
echo "   Web Interface:      python3 app.py"
echo "                       Then open http://localhost:5000"
echo ""
echo "📚 Documentation:      See README.md"
echo "📋 Sample Queries:     See examples/sample_queries.md"
