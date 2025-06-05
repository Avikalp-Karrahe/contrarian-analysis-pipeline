# Data Directory

This directory contains the data storage structure for the Contrarian Analysis Pipeline.

## Directory Structure

```
data/
├── master_contrarian_db/           # Master contrarian analyst database
│   ├── master_contrarian_database.csv  # Main database file (created on first run)
│   └── author_histories/               # Individual author history files
└── run_outputs/                    # Pipeline run outputs
    └── RUN_YYYYMMDD_HHMMSS/       # Run-specific directories (created automatically)
        ├── articles_summary_dashboard.csv
        ├── author_statistics.csv
        └── run_metadata.json
```

## Notes

- The `master_contrarian_database.csv` file will be created automatically on the first pipeline run
- Each pipeline run creates a new timestamped directory in `run_outputs/`
- Author history files are created automatically as new authors are detected
- This directory structure is essential for the pipeline to function correctly

## Getting Started

No manual setup is required for this directory. The pipeline will create all necessary files and subdirectories automatically when you run it for the first time.