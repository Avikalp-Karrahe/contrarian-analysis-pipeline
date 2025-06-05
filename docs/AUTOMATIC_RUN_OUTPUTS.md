# Automatic Run Output Generation

This document explains the automatic generation of run-specific output folders and CSV files whenever the pipeline runs.

## Overview

Every time the automated pipeline executes, it now automatically creates:

1. **Run-specific folder** in `data/run_outputs/RUN_YYYYMMDD_HHMMSS/`
2. **Articles summary dashboard CSV** with detailed analysis results
3. **Author statistics CSV** with performance metrics
4. **Run metadata JSON** with execution details

## Generated Files Structure

```
data/run_outputs/
├── RUN_20240120_143022/
│   ├── articles_summary_dashboard.csv
│   ├── author_statistics.csv
│   └── run_metadata.json
├── RUN_20240120_150815/
│   ├── articles_summary_dashboard.csv
│   ├── author_statistics.csv
│   └── run_metadata.json
└── ...
```

## File Contents

### 1. Articles Summary Dashboard (`articles_summary_dashboard.csv`)

Contains detailed information for each article processed:

| Column | Description |
|--------|-------------|
| `Article_ID` | Unique article identifier |
| `Article_Link` | URL to the original article |
| `Author` | Article author name |
| `Publication_Date` | When the article was published |
| `Company_Ticker` | Stock ticker symbol |
| `Article_Title` | Article headline |
| `Article_Summary` | Brief summary of article content |
| `Analysis_Summary` | Summary of sentiment analysis |
| `Author_Summary` | Author background and track record |
| `Author_Prediction` | Author's prediction (Positive/Negative/Neutral) |
| `Market_Consensus` | General market sentiment |
| `Contrarian_Status` | Whether this is a contrarian view |
| `Sentiment_Score` | Numerical sentiment score (-1 to 1) |
| `EPS_Actual` | Actual earnings per share |
| `EPS_Expected` | Expected earnings per share |
| `EPS_Surprise` | Difference between actual and expected |
| `EPS_Surprise_Percentage` | Surprise as percentage |
| `Investment_Signal` | Generated signal (BUY/SELL/HOLD) |
| `Signal_Confidence` | Confidence level (0-1) |
| `Processing_Status` | Processing status |

### 2. Author Statistics (`author_statistics.csv`)

Contains performance metrics for each author:

| Column | Description |
|--------|-------------|
| `Author_Name` | Author's name |
| `Total_Articles` | Total articles by this author |
| `Contrarian_Articles` | Number of contrarian articles |
| `Contrarian_Rate` | Percentage of contrarian articles |
| `Prediction_Accuracy` | Overall prediction accuracy |
| `Contrarian_Accuracy` | Accuracy of contrarian predictions |
| `Companies_Covered` | Number of companies covered |
| `Primary_Specialization` | Author's area of expertise |
| `Recent_Performance_30d` | Performance in last 30 days |
| `Recent_Performance_90d` | Performance in last 90 days |
| `Average_Sentiment_Score` | Average sentiment of articles |
| `EPS_Surprise_Correlation` | Correlation with EPS surprises |
| `Signal_Success_Rate` | Success rate of investment signals |
| `Last_Article_Date` | Date of most recent article |
| `Author_Reliability_Score` | Overall reliability score |

### 3. Run Metadata (`run_metadata.json`)

Contains execution details and system information:

```json
{
  "run_id": "RUN_20240120_143022",
  "start_time": "2024-01-20T14:30:22",
  "end_time": "2024-01-20T14:32:45",
  "duration_seconds": 143,
  "script_name": "automated_pipeline.py",
  "config_file": "pipeline_config.yaml",
  "target_companies": ["AAPL"],
  "analysis_type": "full_pipeline",
  "total_articles_processed": 25,
  "contrarians_identified": 8,
  "success_rate": 1.0,
  "errors_encountered": [],
  "output_files": ["articles_summary_dashboard.csv", "author_statistics.csv"],
  "pipeline_version": "1.0",
  "system_info": {
    "python_version": "3.9.0",
    "platform": "macOS",
    "memory_usage_mb": 256,
    "cpu_usage_percent": 15.2
  }
}
```

## How It Works

### 1. Integration with Pipeline

The `RunOutputGenerator` class is integrated into the main `AutomatedPipeline`:

```python
# In automated_pipeline.py
from run_output_generator import RunOutputGenerator

class AutomatedPipeline:
    def __init__(self, config_path: str = 'pipeline_config.yaml'):
        # ... other initialization ...
        self.run_output_generator = RunOutputGenerator()
```

### 2. Automatic Execution

Every time `run_full_pipeline()` is called:

1. **Run tracking starts** - Captures start time, configuration
2. **Data collection** - Gathers articles and author information
3. **Pipeline execution** - Runs all analysis steps
4. **Output generation** - Creates run-specific folder and CSV files
5. **Finalization** - Logs completion and file locations

### 3. Data Collection

The pipeline automatically collects:

- **Article data** from Guardian API results
- **Sentiment analysis** results from Llama3 processing
- **Author information** extracted from articles
- **Performance metrics** calculated during execution
- **Error tracking** for debugging and quality assurance

## Usage Examples

### Running the Pipeline

```bash
# Standard pipeline run
python src/core/automated_pipeline.py

# Force refresh all data
python src/core/automated_pipeline.py --force-refresh

# Verbose logging
python src/core/automated_pipeline.py --verbose
```

### Testing Output Generation

```bash
# Test the output generation system
python scripts/test_run_output_generation.py
```

### Accessing Generated Data

```python
import pandas as pd
from pathlib import Path

# Load latest run data
run_outputs_dir = Path('data/run_outputs')
latest_run = max(run_outputs_dir.glob('RUN_*'))

# Load articles dashboard
articles_df = pd.read_csv(latest_run / 'articles_summary_dashboard.csv')
print(f"Processed {len(articles_df)} articles")

# Load author statistics
authors_df = pd.read_csv(latest_run / 'author_statistics.csv')
print(f"Analyzed {len(authors_df)} authors")

# Load run metadata
import json
with open(latest_run / 'run_metadata.json') as f:
    metadata = json.load(f)
print(f"Run duration: {metadata['duration_seconds']} seconds")
```

## Business Intelligence Integration

### Excel/Google Sheets

1. Open the CSV files directly in Excel or Google Sheets
2. Create pivot tables for analysis
3. Build charts and dashboards

### Power BI / Tableau

1. Connect to the CSV files as data sources
2. Set up automatic refresh from the run_outputs folder
3. Create interactive dashboards

### Python Analysis

```python
# Combine multiple runs for trend analysis
import pandas as pd
from pathlib import Path

all_runs = []
for run_dir in Path('data/run_outputs').glob('RUN_*'):
    articles_file = run_dir / 'articles_summary_dashboard.csv'
    if articles_file.exists():
        df = pd.read_csv(articles_file)
        df['run_id'] = run_dir.name
        all_runs.append(df)

combined_df = pd.concat(all_runs, ignore_index=True)
print(f"Total articles across all runs: {len(combined_df)}")
```

## Key Features

### ✅ Automatic Generation
- No manual intervention required
- Runs every time the pipeline executes
- Consistent file structure and naming

### ✅ Comprehensive Data
- Complete article analysis pipeline
- Author performance tracking
- EPS surprise analysis
- Investment signal generation

### ✅ Business Ready
- CSV format for easy import
- Structured data for BI tools
- Metadata for audit trails

### ✅ Scalable
- Handles multiple companies
- Supports large datasets
- Efficient file organization

### ✅ Error Handling
- Graceful failure handling
- Partial data generation on errors
- Comprehensive error logging

## Configuration

### Custom Output Directory

```python
# Use custom output directory
generator = RunOutputGenerator('/custom/path/to/outputs')
```

### Data Integration

The system automatically integrates with existing pipeline data files:

- `data/guardian_articles.csv` - Article data
- `data/sentiment_analysis.csv` - Sentiment results
- `data/contrarian_analysis.csv` - Contrarian indicators

## Monitoring and Maintenance

### Disk Space Management

```bash
# Check run outputs size
du -sh data/run_outputs/

# Clean old runs (keep last 30 days)
find data/run_outputs/ -name "RUN_*" -mtime +30 -exec rm -rf {} \;
```

### Quality Checks

```python
# Verify recent runs
from pathlib import Path
import pandas as pd

for run_dir in sorted(Path('data/run_outputs').glob('RUN_*'))[-5:]:
    articles_file = run_dir / 'articles_summary_dashboard.csv'
    if articles_file.exists():
        df = pd.read_csv(articles_file)
        print(f"{run_dir.name}: {len(df)} articles")
```

## Troubleshooting

### Common Issues

1. **Empty CSV files**: Check if pipeline data sources exist
2. **Missing run folders**: Verify write permissions on data/run_outputs
3. **Incomplete data**: Check pipeline logs for errors

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test output generation
from src.core.run_output_generator import RunOutputGenerator
generator = RunOutputGenerator()
result = generator.process_pipeline_run()
```

## Future Enhancements

- **Real-time dashboard updates**
- **Email notifications on completion**
- **Automated data quality checks**
- **Integration with cloud storage**
- **Advanced analytics and ML insights**

---

*This automatic output generation ensures that every pipeline run produces comprehensive, business-ready data for analysis and decision-making.*