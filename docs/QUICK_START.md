# 🚀 Quick Start Guide - Automated Sentiment Analysis Pipeline

This guide will get you up and running with the automated sentiment analysis pipeline in just a few minutes.

## ✅ Prerequisites

- Python 3.8+ installed
- Your existing Jupyter notebooks in the project directory
- Guardian API access (if using Guardian API)

## 🔧 Setup (One-time)

### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv automation_env

# Activate it (Linux/Mac)
source automation_env/bin/activate

# Or use the convenience script
./activate_automation.sh
```

### Step 2: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 3: Validate Setup
```bash
# Run full setup validation
python setup_automation.py --full-setup
```

## 🎯 Quick Test

### Test Configuration
```bash
# Check if everything is configured correctly
python automated_pipeline.py --dry-run
```

### Run Pipeline Once
```bash
# Execute the complete pipeline
python automated_pipeline.py
```

## 📊 What Happens When You Run the Pipeline?

1. **Data Collection** 📰
   - Checks if article data is fresh (< 6 hours old)
   - If stale, runs `Guardian_API.ipynb` to fetch new articles
   - Saves articles to `apple_articles_with_body.xlsx`

2. **Sentiment Analysis** 🧠
   - Checks if sentiment data is fresh (< 6 hours old)
   - If stale, runs `Sentiment analysis using lama.ipynb`
   - Processes articles through Llama3 model
   - Saves results to `sentiment_output.csv`

3. **Contrarian Analysis** 📈
   - Runs `apple_contraian.ipynb`
   - Analyzes EPS surprises and stock performance
   - Generates contrarian investment insights

4. **Signal Generation** 🎯
   - Calculates sentiment distribution
   - Generates investment signals:
     - **STRONG_BUY**: >60% negative sentiment
     - **WEAK_BUY**: 40-60% negative sentiment
     - **CAUTION**: >70% positive sentiment
     - **NEUTRAL**: Balanced sentiment
   - Saves detailed report to `reports/investment_signal_*.json`

## 🔄 Automation Options

### Option 1: Manual Execution
```bash
# Run whenever you want
python automated_pipeline.py

# Force refresh all data
python automated_pipeline.py --force-refresh
```

### Option 2: Scheduled Execution
```bash
# Start scheduler daemon (runs based on config)
python pipeline_scheduler.py --daemon

# Run once via scheduler
python pipeline_scheduler.py --once

# Check scheduler status
python pipeline_scheduler.py --status
```

### Option 3: Cron Job
```bash
# Get cron setup instructions
python pipeline_scheduler.py --create-cron

# Example: Run every 6 hours
# Add to crontab: 0 */6 * * * /path/to/automation_env/bin/python /path/to/pipeline_scheduler.py --once
```

## ⚙️ Configuration

Edit `pipeline_config.yaml` to customize:

```yaml
# Data freshness (how often to refresh)
data_collection:
  max_age_hours: 6  # Refresh articles every 6 hours

sentiment_analysis:
  max_age_hours: 6  # Refresh sentiment every 6 hours

# Investment signal thresholds
signal_generation:
  thresholds:
    strong_negative_ratio: 0.6  # 60%+ negative = STRONG_BUY
    weak_negative_ratio: 0.4    # 40-60% negative = WEAK_BUY
    strong_positive_ratio: 0.7  # 70%+ positive = CAUTION

# Scheduling
scheduling:
  enabled: true
  daily_run_time: "09:00"  # Run at 9 AM daily
  interval_hours: 6        # Also run every 6 hours
```

## 📁 Key Files

| File | Purpose |
|------|----------|
| `automated_pipeline.py` | Main automation script |
| `pipeline_scheduler.py` | Scheduling system |
| `pipeline_config.yaml` | Configuration settings |
| `setup_automation.py` | Setup and validation |
| `activate_automation.sh` | Environment activation |
| `logs/pipeline_v0.log` | Execution logs |
| `reports/investment_signal_*.json` | Generated signals |

## 📊 Sample Output

### Investment Signal Report
```json
{
  "timestamp": "2024-01-15T14:30:00",
  "signal": "STRONG_BUY",
  "confidence": "HIGH",
  "reasoning": "High negative sentiment (65%) suggests contrarian opportunity",
  "sentiment_distribution": {
    "positive": 0.20,
    "negative": 0.65,
    "neutral": 0.15,
    "total_articles": 87
  }
}
```

### Log Output
```
2024-01-15 14:30:00 - AutomatedPipeline - INFO - Starting automated pipeline execution
2024-01-15 14:30:05 - AutomatedPipeline - INFO - Skipping data collection - articles are fresh
2024-01-15 14:30:05 - AutomatedPipeline - INFO - Starting sentiment analysis phase
2024-01-15 14:32:15 - AutomatedPipeline - INFO - Sentiment analysis completed successfully
2024-01-15 14:32:20 - AutomatedPipeline - INFO - Investment Signal: STRONG_BUY (Confidence: HIGH)
2024-01-15 14:32:20 - AutomatedPipeline - INFO - Pipeline completed successfully in 0:02:20
```

## 🔍 Monitoring

### View Real-time Logs
```bash
# Monitor pipeline execution
tail -f logs/pipeline_v0.log

# Check for errors
grep ERROR logs/pipeline_v0.log

# View recent activity
tail -20 logs/pipeline_v0.log
```

### Check Data Status
```bash
# Check file timestamps
ls -la Llama3_SentimentAnalysis/
ls -la reports/

# View latest signal
cat reports/investment_signal_*.json | tail -1 | python -m json.tool
```

## 🚨 Troubleshooting

### Common Issues

**Issue**: Module not found errors
```bash
# Solution: Ensure virtual environment is activated
source automation_env/bin/activate
# Or use: ./activate_automation.sh
```

**Issue**: Notebook execution fails
```bash
# Solution: Check notebook paths in config
python automated_pipeline.py --dry-run

# Test notebook manually
jupyter nbconvert --execute --inplace "path/to/notebook.ipynb"
```

**Issue**: No signals generated
```bash
# Solution: Check sentiment data
head Llama3_SentimentAnalysis/sentiment_output.csv

# Force refresh
python automated_pipeline.py --force-refresh
```

**Issue**: Permission errors
```bash
# Solution: Check file permissions
chmod +x activate_automation.sh
chmod 755 logs/ reports/
```

## 🎯 Next Steps

1. **Customize Configuration**: Edit `pipeline_config.yaml` for your needs
2. **Set Up Notifications**: Configure email/Slack alerts in config
3. **Add More Companies**: Extend config for multiple stock analysis
4. **Integrate Trading**: Connect signals to trading platforms
5. **Monitor Performance**: Set up regular log reviews

## 📞 Quick Commands Reference

```bash
# Environment
./activate_automation.sh          # Activate environment
deactivate                        # Deactivate environment

# Testing
python setup_automation.py --full-setup    # Validate setup
python automated_pipeline.py --dry-run     # Test configuration

# Execution
python automated_pipeline.py               # Run once
python automated_pipeline.py --force-refresh  # Force refresh

# Scheduling
python pipeline_scheduler.py --daemon      # Start scheduler
python pipeline_scheduler.py --once        # Single scheduled run
python pipeline_scheduler.py --status      # Check status

# Monitoring
tail -f logs/pipeline_v0.log              # Live logs
grep ERROR logs/pipeline_v0.log            # Check errors
ls -la reports/                            # View reports
```

---

**🎉 You're all set!** The automation system will now handle your sentiment analysis workflow, from data collection to investment signal generation, with minimal manual intervention.

For detailed documentation, see `README_AUTOMATION.md`.