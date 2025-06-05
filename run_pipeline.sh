#!/bin/bash

# Contrarian Analysis Pipeline Runner
# This script handles all the necessary setup to run the pipeline properly

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting Contrarian Analysis Pipeline..."
echo "📁 Working directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r config/requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your API keys:"
    echo "   GUARDIAN_API_KEY=your_guardian_key_here"
    echo "   GROQ_API_KEY=your_groq_key_here"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Set up Python path
export PYTHONPATH="$PYTHONPATH:$SCRIPT_DIR/src/analyzers"

# Function to run production analysis
run_production() {
    echo "📊 Running production contrarian analysis..."
    python3 scripts/run_production_contrarian_analysis.py "$@"
}

# Function to run demo
run_demo() {
    echo "🧪 Running demo analysis..."
    python3 demos/demo_simplified_contrarian.py
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [demo|production] [options]"
    echo ""
    echo "Commands:"
    echo "  demo                    Run the simplified demo"
    echo "  production [options]    Run production analysis with options"
    echo ""
    echo "Production options:"
    echo "  --company COMPANY       Company name (required)"
    echo "  --symbol SYMBOL         Stock symbol (required)"
    echo "  --date DATE             Earnings date YYYY-MM-DD (required)"
    echo "  --days DAYS             Days before earnings to analyze (default: 30)"
    echo "  --max-articles NUM      Maximum articles to collect (default: 20)"
    echo "  --conservative          Use conservative rate limiting"
    echo "  --force                 Skip confirmation prompts"
    echo "  --verbose               Enable verbose logging"
    echo "  --quiet                 Suppress non-essential output"
    echo ""
    echo "Examples:"
    echo "  $0 demo"
    echo "  $0 production --company \"Apple Inc.\" --symbol AAPL --date 2024-11-01 --force"
    echo "  $0 production --company \"Microsoft\" --symbol MSFT --date 2024-10-24 --days 45 --max-articles 40"
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

COMMAND="$1"
shift

case "$COMMAND" in
    "demo")
        run_demo
        ;;
    "production")
        if [ $# -eq 0 ]; then
            echo "❌ Production mode requires additional arguments"
            show_usage
            exit 1
        fi
        run_production "$@"
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

echo "✅ Pipeline execution completed!"