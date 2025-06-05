# Contrarian Earnings Analysis System

A comprehensive system for identifying and tracking contrarian financial analysts who consistently oppose market consensus during earnings announcements.

## 📁 Project Structure

```
├── src/                           # Source code
│   ├── analyzers/                 # Core analysis components
│   │   ├── simplified_contrarian_analyzer.py
│   │   ├── contrarian_earnings_analyzer.py
│   │   ├── contrarian_earnings_analyzer_production.py
│   │   ├── master_contrarian_database.py
│   │   └── contrarian_csv_exporter.py
│   └── core/                      # Core system components
│       ├── automated_pipeline.py
│       ├── pipeline_scheduler.py
│       └── setup_automation.py
├── demos/                         # Demo scripts
│   ├── demo_google_earnings_pipeline.py
│   ├── demo_google_earnings_realistic.py
│   ├── demo_master_contrarian_tracking.py
│   └── demo_simplified_contrarian.py
├── scripts/                       # Utility scripts
│   ├── run_contrarian_analysis.py
│   ├── run_contrarian_with_csv.py
│   ├── run_production_contrarian_analysis.py
│   └── activate_automation.sh
├── config/                        # Configuration files
│   ├── pipeline_config.yaml
│   └── requirements.txt
├── docs/                          # Documentation
│   ├── QUICK_START.md
│   ├── README_CONTRARIAN_ANALYSIS.md
│   ├── README_AUTOMATION.md
│   ├── SIMPLIFIED_CONTRARIAN_GUIDE.md
│   └── ...
├── data/                          # Databases and data
│   ├── master_contrarian_db/
│   └── simplified_contrarian_db/
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

2. **Run a Demo**
   ```bash
   python demos/demo_simplified_contrarian.py
   ```

3. **View Results**
   - Check `data/simplified_contrarian_db/` for analysis results
   - Review `data/master_contrarian_db/` for author tracking

## 📖 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started quickly
- **[Contrarian Analysis Guide](docs/README_CONTRARIAN_ANALYSIS.md)** - Core analysis concepts
- **[Automation Guide](docs/README_AUTOMATION.md)** - Automation setup
- **[Simplified Guide](docs/SIMPLIFIED_CONTRARIAN_GUIDE.md)** - Simplified system usage

## 🎯 Key Features

- **Contrarian Identification**: Automatically identifies analysts who oppose market consensus
- **Performance Tracking**: Tracks accuracy and performance of contrarian analysts
- **Investment Signals**: Generates buy/sell signals based on contrarian analysis
- **Automated Pipeline**: Fully automated analysis pipeline
- **Multiple Data Sources**: Supports Guardian API, CSV imports, and more

## 🔧 Core Components

### Analyzers (`src/analyzers/`)
- **SimplifiedContrarianAnalyzer**: Streamlined analysis engine
- **ContrarianEarningsAnalyzer**: Full-featured analysis system
- **MasterContrarianDatabase**: Author tracking and history management

### Automation (`src/core/`)
- **AutomatedPipeline**: Main automation orchestrator
- **PipelineScheduler**: Scheduling and timing management
- **SetupAutomation**: System setup and configuration

## 📊 Data Structure

### Contrarian Records
- Author information and predictions
- Sentiment analysis results
- Accuracy tracking
- Investment signals

### Author Statistics
- Historical performance metrics
- Contrarian accuracy rates
- Company specializations
- Recent performance streaks

## 🛠️ Usage Examples

### Basic Analysis
```python
from src.analyzers.simplified_contrarian_analyzer import SimplifiedContrarianAnalyzer

analyzer = SimplifiedContrarianAnalyzer()
results = analyzer.analyze_company_earnings("GOOGL", "2024-01-01")
```

### Automated Pipeline
```bash
python src/core/automated_pipeline.py --company GOOGL --date 2024-01-01
```

## 📈 Results

The system has successfully:
- Identified contrarian analysts with 66.7% accuracy
- Generated investment signals for major tech companies
- Tracked 10+ financial analysts across multiple companies
- Processed earnings data for Apple, Google, Microsoft, and more

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure all demos work correctly

## 📄 License

This project is for educational and research purposes.