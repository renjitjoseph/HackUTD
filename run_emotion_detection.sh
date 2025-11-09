#!/bin/bash
# Script to run the Facial Sentiment Analyzer

echo "🎭 Starting Facial Sentiment Analyzer..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the application
python facial_sentiment_analyzer.py

