# Contrarian Analysis Pipeline - Usage Guide

## 🚀 Quick Start

The pipeline is now fully functional with an easy-to-use runner script that handles all the technical setup automatically.

### Prerequisites

1. **API Keys Required:**
   - Guardian API Key: Get from https://open-platform.theguardian.com/access/
   - Groq API Key: Get from https://console.groq.com/

2. **Environment Setup:**
   ```bash
   # Create virtual environment (if not already done)
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Install dependencies
   pip install -r config/requirements.txt
   ```

3. **Configure API Keys:**
   Edit the `.env` file in the project root:
   ```
   GUARDIAN_API_KEY=your_guardian_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

## 🎯 Running the Pipeline

### Option 1: Demo Mode (Quick Test)
```bash
./run_pipeline.sh demo
```
This runs a simplified analysis on test data to verify everything is working.

### Option 2: Production Analysis
```bash
./run_pipeline.sh production --company "Apple Inc." --symbol "AAPL" --date "2024-11-01" --force
```

## 📊 Production Analysis Options

### Required Parameters:
- `--company`: Company name (e.g., "Apple Inc.", "Microsoft Corporation")
- `--symbol`: Stock ticker symbol (e.g., "AAPL", "MSFT")
- `--date`: Earnings date in YYYY-MM-DD format

### Optional Parameters:
- `--days`: Days before earnings to analyze (default: 30)
- `--max-articles`: Maximum articles to collect (default: 20)
- `--conservative`: Use conservative rate limiting for APIs
- `--force`: Skip confirmation prompts
- `--verbose`: Enable detailed logging
- `--quiet`: Suppress non-essential output

## 📈 Example Commands

### Basic Analysis
```bash
./run_pipeline.sh production --company "Apple Inc." --symbol "AAPL" --date "2024-11-01" --force
```

### Extended Analysis
```bash
./run_pipeline.sh production --company "Microsoft Corporation" --symbol "MSFT" --date "2024-10-24" --days 45 --max-articles 40 --verbose
```

### Conservative Mode (Slower but Safer)
```bash
./run_pipeline.sh production --company "Tesla Inc." --symbol "TSLA" --date "2024-10-23" --conservative --force
```

## 📁 Output Files

The pipeline generates several types of output:

### 1. JSON Reports
- Location: `reports/contrarian_analysis_[SYMBOL]_[TIMESTAMP].json`
- Contains: Complete analysis results, article data, sentiment scores, contrarian findings

### 2. CSV Databases
- `simplified_contrarian_db/contrarian_records.csv`: Historical contrarian predictions
- `simplified_contrarian_db/author_statistics.csv`: Author performance tracking

### 3. Log Files
- `contrarian_analysis.log`: Production analysis logs
- `simplified_contrarian_analysis.log`: Demo analysis logs

## 🔍 Understanding Results

### Contrarian Analysis Output
```
CONTRARIAN ANALYSIS:
  Contrarians found: 2
  Top contrarians:
    1. John Smith (Score: 85.5) - Predicted: miss, Sentiment: bearish
    2. Jane Doe (Score: 78.2) - Predicted: beat, Sentiment: bullish
```

### Market Consensus
```
MARKET CONSENSUS:
  Sentiment distribution: {'bullish': 12, 'bearish': 3, 'neutral': 5}
  Prediction distribution: {'beat': 15, 'meet': 3, 'miss': 2}
```

## 🛠 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: The runner script automatically handles Python path issues
2. **API Authentication Errors**: Check your `.env` file has valid API keys
3. **Rate Limiting**: Use `--conservative` flag for slower but more reliable execution
4. **No Articles Found**: Try increasing `--days` parameter or different date ranges

### Getting Help
```bash
./run_pipeline.sh help
```

## 🔧 Advanced Usage

### Manual Execution (if needed)
If you prefer to run components manually:

```bash
# Activate environment and set Python path
source venv/bin/activate
export PYTHONPATH="$PYTHONPATH:src/analyzers"

# Run production analysis
python3 scripts/run_production_contrarian_analysis.py --company "Apple Inc." --symbol "AAPL" --date "2024-11-01" --force

# Run demo
python3 demos/demo_simplified_contrarian.py
```

## 📊 Pipeline Features

✅ **Fully Automated**: One command runs the entire analysis
✅ **Error Handling**: Comprehensive error checking and user-friendly messages
✅ **Rate Limiting**: Respects API limits with configurable delays
✅ **Data Persistence**: Saves results in multiple formats
✅ **Logging**: Detailed logs for debugging and monitoring
✅ **Flexible Configuration**: Customizable parameters for different use cases

## 🎯 Next Steps

1. **Run Demo**: Start with `./run_pipeline.sh demo` to verify setup
2. **Test Production**: Try a simple production analysis
3. **Explore Results**: Check the generated reports and CSV files
4. **Customize**: Adjust parameters for your specific analysis needs

The pipeline is now ready for production use! 🚀