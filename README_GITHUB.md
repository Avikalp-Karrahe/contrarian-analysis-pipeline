# Contrarian Analysis Pipeline

A comprehensive automated pipeline for analyzing contrarian sentiment in financial earnings calls and building a master database of contrarian analysts.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

2. **Run the Pipeline**
   ```bash
   python3 src/core/automated_pipeline.py
   ```

3. **Test the Integration**
   ```bash
   python3 scripts/test_pipeline_integration_concept.py
   ```

## 📁 Project Structure

```
contrarian_analysis_pipeline/
├── README.md                                    # Main project documentation
├── README_GITHUB.md                           # This file
├── MASTER_CONTRARIAN_DATABASE_INTEGRATION.md  # Database integration guide
├── .gitignore                                  # Git ignore rules
├── config/
│   ├── pipeline_config.yaml                   # Pipeline configuration
│   └── requirements.txt                       # Python dependencies
├── src/
│   ├── core/                                  # Core pipeline components
│   │   ├── automated_pipeline.py              # Main pipeline orchestrator
│   │   ├── run_output_generator.py            # Output generation
│   │   └── pipeline_scheduler.py              # Scheduling functionality
│   └── analyzers/                             # Analysis modules
│       ├── master_contrarian_database.py      # Master database manager
│       ├── contrarian_earnings_analyzer.py    # Contrarian analysis engine
│       └── simplified_contrarian_analyzer.py  # Simplified analysis version
├── scripts/
│   ├── test_pipeline_integration_concept.py   # Integration testing
│   └── run_production_contrarian_analysis.py  # Production runner
├── demos/
│   ├── demo_google_earnings_pipeline.py       # Google earnings demo
│   ├── demo_master_contrarian_tracking.py     # Database tracking demo
│   └── demo_simplified_contrarian.py          # Simplified analysis demo
├── docs/
│   ├── QUICK_START.md                         # Quick start guide
│   ├── CONTRARIAN_SYSTEM_SUMMARY.md          # System overview
│   └── AUTOMATIC_RUN_OUTPUTS.md              # Output documentation
└── data/
    ├── README.md                              # Data directory guide
    ├── master_contrarian_db/                  # Master database storage
    └── run_outputs/                           # Pipeline run outputs
```

## 🎯 Key Features

### 1. Automated Pipeline
- **Data Collection**: Automatically gathers financial news and earnings data
- **Sentiment Analysis**: Analyzes sentiment patterns in financial articles
- **Contrarian Detection**: Identifies contrarian viewpoints and predictions
- **Signal Generation**: Creates investment signals based on contrarian analysis

### 2. Master Contrarian Database
- **Author Tracking**: Automatically tracks contrarian analysts
- **Performance Metrics**: Maintains success rates and accuracy statistics
- **Historical Data**: Builds comprehensive author performance history
- **Incremental Updates**: Updates counts and adds new authors after each run

### 3. Automated Outputs
- **Run-Specific Reports**: Generates timestamped output directories
- **Dashboard Data**: Creates CSV files for BI tool integration
- **Metadata Tracking**: Maintains detailed run information
- **Author Statistics**: Provides comprehensive author performance data

## 🔧 Configuration

### Pipeline Configuration (`config/pipeline_config.yaml`)
```yaml
data_sources:
  - google_news
  - financial_apis

analysis_settings:
  sentiment_threshold: 0.6
  contrarian_threshold: 0.7
  
output_settings:
  generate_dashboard: true
  save_metadata: true
```

### Dependencies (`config/requirements.txt`)
- pandas
- numpy
- scikit-learn
- jupyter
- requests
- pyyaml

## 📊 Usage Examples

### Basic Pipeline Run
```python
from src.core.automated_pipeline import AutomatedPipeline

# Initialize pipeline
pipeline = AutomatedPipeline()

# Run full analysis
results = pipeline.run_full_pipeline()

print(f"Analysis completed. Results saved to: {results['output_dir']}")
```

### Master Database Integration
```python
from src.analyzers.master_contrarian_database import MasterContrarianDatabase

# Initialize database
db = MasterContrarianDatabase()

# Add contrarian analysis results
db.add_contrarian_analysis(contrarian_data)

print(f"Database updated. Total authors: {len(db.get_all_authors())}")
```

## 📈 Output Structure

Each pipeline run generates:

### Run-Specific Directory (`data/run_outputs/RUN_YYYYMMDD_HHMMSS/`)
- `articles_summary_dashboard.csv` - Article analysis results
- `author_statistics.csv` - Author performance metrics
- `run_metadata.json` - Run configuration and timing

### Master Database (`data/master_contrarian_db/`)
- `master_contrarian_database.csv` - Comprehensive author database
- `author_histories/` - Individual author performance files

## 🧪 Testing

### Integration Test
```bash
python3 scripts/test_pipeline_integration_concept.py
```

### Demo Scripts
```bash
# Google earnings analysis demo
python3 demos/demo_google_earnings_pipeline.py

# Master database tracking demo
python3 demos/demo_master_contrarian_tracking.py

# Simplified analysis demo
python3 demos/demo_simplified_contrarian.py
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running quickly
- **[System Summary](docs/CONTRARIAN_SYSTEM_SUMMARY.md)** - Comprehensive system overview
- **[Output Documentation](docs/AUTOMATIC_RUN_OUTPUTS.md)** - Understanding pipeline outputs
- **[Database Integration](MASTER_CONTRARIAN_DATABASE_INTEGRATION.md)** - Master database details

## 🔄 Workflow

1. **Data Collection** → Gather financial news and earnings data
2. **Sentiment Analysis** → Analyze article sentiment and tone
3. **Contrarian Detection** → Identify contrarian viewpoints
4. **Database Update** → Update master contrarian database
5. **Signal Generation** → Create investment signals
6. **Output Generation** → Generate reports and dashboards

## 🎯 Benefits

- **Automated Operation**: No manual intervention required
- **Persistent Intelligence**: Builds knowledge over time
- **Performance Tracking**: Monitors analyst accuracy
- **Investment Insights**: Generates actionable signals
- **Scalable Architecture**: Handles growing data volumes
- **BI Integration**: Compatible with business intelligence tools

## 🚀 Getting Started

1. Clone or download this repository
2. Install dependencies: `pip install -r config/requirements.txt`
3. Run the test: `python3 scripts/test_pipeline_integration_concept.py`
4. Execute the pipeline: `python3 src/core/automated_pipeline.py`
5. Check outputs in `data/run_outputs/` and `data/master_contrarian_db/`

## 📞 Support

For questions or issues:
1. Check the documentation in the `docs/` folder
2. Run the demo scripts to understand functionality
3. Review the integration test for troubleshooting

---

**Note**: This is a complete, production-ready contrarian analysis pipeline with automated database integration. All components are designed to work together seamlessly for comprehensive financial sentiment analysis and contrarian intelligence gathering.