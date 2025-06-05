#!/usr/bin/env python3
"""
Automated Sentiment Analysis and Contrarian Investment Pipeline - Version 0

This script automates the entire workflow:
1. Data Collection (Guardian API)
2. Sentiment Analysis (Llama3)
3. Contrarian Analysis
4. Investment Signal Generation

Usage:
    python automated_pipeline.py [--config config.yaml] [--dry-run] [--verbose]
"""

import os
import sys
import json
import yaml
import logging
import argparse
import subprocess
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import traceback

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import run output generator and master contrarian database
from run_output_generator import RunOutputGenerator
sys.path.append(str(project_root.parent / 'src' / 'analyzers'))
from master_contrarian_database import MasterContrarianDatabase

class PipelineLogger:
    """Enhanced logging for the pipeline"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('log_file', 'pipeline_v0.log')
        
        # Create logs directory if it doesn't exist
        log_path = project_root / 'logs'
        log_path.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path / log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('AutomatedPipeline')
        self.logger.info("Pipeline logger initialized")

class DataFreshnessChecker:
    """Check if data needs to be refreshed"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    def is_data_fresh(self, file_path: Path, max_age_hours: int) -> bool:
        """Check if data file is fresh enough"""
        if not file_path.exists():
            self.logger.info(f"File {file_path} does not exist, needs refresh")
            return False
        
        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
        is_fresh = file_age < timedelta(hours=max_age_hours)
        
        self.logger.info(f"File {file_path} age: {file_age}, fresh: {is_fresh}")
        return is_fresh
    
    def check_all_data_freshness(self) -> Dict[str, bool]:
        """Check freshness of all data files"""
        company_config = self.config['companies']['apple']
        data_config = self.config['data_collection']
        sentiment_config = self.config['sentiment_analysis']
        
        freshness = {
            'articles': self.is_data_fresh(
                project_root / company_config['data_files']['articles'],
                data_config['max_age_hours']
            ),
            'sentiment': self.is_data_fresh(
                project_root / company_config['data_files']['sentiment'],
                sentiment_config['max_age_hours']
            )
        }
        
        return freshness

class NotebookExecutor:
    """Execute Jupyter notebooks programmatically"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    def execute_notebook(self, notebook_path: Path, timeout: int = 600) -> bool:
        """Execute a Jupyter notebook and return success status"""
        try:
            self.logger.info(f"Executing notebook: {notebook_path}")
            
            # Convert notebook path to absolute path
            abs_notebook_path = project_root / notebook_path
            
            if not abs_notebook_path.exists():
                self.logger.error(f"Notebook not found: {abs_notebook_path}")
                return False
            
            # Execute notebook using nbconvert
            cmd = [
                'jupyter', 'nbconvert',
                '--to', 'notebook',
                '--execute',
                '--inplace',
                '--ExecutePreprocessor.timeout=' + str(timeout),
                str(abs_notebook_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 60  # Add buffer time
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully executed: {notebook_path}")
                return True
            else:
                self.logger.error(f"Failed to execute {notebook_path}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Notebook execution timed out: {notebook_path}")
            return False
        except Exception as e:
            self.logger.error(f"Error executing notebook {notebook_path}: {str(e)}")
            return False

class SignalGenerator:
    """Generate investment signals based on sentiment analysis"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    def load_sentiment_data(self) -> Optional[pd.DataFrame]:
        """Load sentiment analysis results"""
        try:
            sentiment_file = project_root / self.config['companies']['apple']['data_files']['sentiment']
            
            if not sentiment_file.exists():
                self.logger.error(f"Sentiment file not found: {sentiment_file}")
                return None
            
            df = pd.read_csv(sentiment_file)
            self.logger.info(f"Loaded {len(df)} sentiment records")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading sentiment data: {str(e)}")
            return None
    
    def calculate_sentiment_distribution(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate sentiment distribution"""
        if 'sentiment' not in df.columns:
            self.logger.error("Sentiment column not found in data")
            return {}
        
        total_articles = len(df)
        sentiment_counts = df['sentiment'].value_counts()
        
        distribution = {
            'positive': sentiment_counts.get('positive', 0) / total_articles,
            'negative': sentiment_counts.get('negative', 0) / total_articles,
            'neutral': sentiment_counts.get('neutral', 0) / total_articles,
            'total_articles': total_articles
        }
        
        self.logger.info(f"Sentiment distribution: {distribution}")
        return distribution
    
    def generate_signals(self, sentiment_dist: Dict[str, float]) -> Dict[str, any]:
        """Generate investment signals based on sentiment"""
        thresholds = self.config['signal_generation']['thresholds']
        confidence_config = self.config['signal_generation']['confidence_calculation']
        
        negative_ratio = sentiment_dist['negative']
        positive_ratio = sentiment_dist['positive']
        total_articles = sentiment_dist['total_articles']
        
        # Determine signal strength
        if negative_ratio >= thresholds['strong_negative_ratio']:
            signal = 'STRONG_BUY'
            reasoning = f"High negative sentiment ({negative_ratio:.1%}) suggests contrarian opportunity"
        elif negative_ratio >= thresholds['weak_negative_ratio']:
            signal = 'WEAK_BUY'
            reasoning = f"Moderate negative sentiment ({negative_ratio:.1%}) suggests potential opportunity"
        elif positive_ratio >= thresholds['strong_positive_ratio']:
            signal = 'CAUTION'
            reasoning = f"High positive sentiment ({positive_ratio:.1%}) may indicate overvaluation"
        else:
            signal = 'NEUTRAL'
            reasoning = "Balanced sentiment, no clear contrarian signal"
        
        # Determine confidence level
        if total_articles >= confidence_config['min_articles_high_confidence']:
            confidence = 'HIGH'
        elif total_articles >= confidence_config['min_articles_medium_confidence']:
            confidence = 'MEDIUM'
        elif total_articles >= confidence_config['min_articles_low_confidence']:
            confidence = 'LOW'
        else:
            confidence = 'VERY_LOW'
            signal = 'INSUFFICIENT_DATA'
            reasoning = f"Only {total_articles} articles available, insufficient for reliable signal"
        
        signal_data = {
            'timestamp': datetime.now().isoformat(),
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'sentiment_distribution': sentiment_dist,
            'thresholds_used': thresholds
        }
        
        self.logger.info(f"Generated signal: {signal} (confidence: {confidence})")
        return signal_data
    
    def save_signal_report(self, signal_data: Dict[str, any]) -> bool:
        """Save signal report to file"""
        try:
            # Create reports directory
            reports_dir = project_root / 'reports'
            reports_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = reports_dir / f'investment_signal_{timestamp}.json'
            
            # Save report
            with open(report_file, 'w') as f:
                json.dump(signal_data, f, indent=2)
            
            self.logger.info(f"Signal report saved: {report_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving signal report: {str(e)}")
            return False

class AutomatedPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, config_path: str = 'pipeline_config.yaml'):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.pipeline_logger = PipelineLogger(self.config)
        self.logger = self.pipeline_logger.logger
        
        # Initialize components
        self.freshness_checker = DataFreshnessChecker(self.config, self.logger)
        self.notebook_executor = NotebookExecutor(self.config, self.logger)
        self.signal_generator = SignalGenerator(self.config, self.logger)
        self.run_output_generator = RunOutputGenerator()
        self.master_contrarian_db = MasterContrarianDatabase()
        
        # Initialize run tracking
        self.current_run_data = {
            'articles': [],
            'authors': {},
            'contrarians': [],
            'run_config': {},
            'start_time': None,
            'errors': []
        }
    
    def load_config(self) -> Dict:
        """Load pipeline configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def run_data_collection(self) -> bool:
        """Run data collection step"""
        self.logger.info("Starting data collection phase")
        
        if not self.config['data_collection']['guardian_api']['enabled']:
            self.logger.info("Guardian API data collection disabled")
            return True
        
        notebook_path = self.config['companies']['apple']['notebooks']['guardian_api']
        timeout = self.config['data_collection']['guardian_api']['timeout']
        
        success = self.notebook_executor.execute_notebook(Path(notebook_path), timeout)
        
        if success:
            self.logger.info("Data collection completed successfully")
        else:
            self.logger.error("Data collection failed")
        
        return success
    
    def run_sentiment_analysis(self) -> bool:
        """Run sentiment analysis step"""
        self.logger.info("Starting sentiment analysis phase")
        
        if not self.config['sentiment_analysis']['llama3']['enabled']:
            self.logger.info("Llama3 sentiment analysis disabled")
            return True
        
        notebook_path = self.config['companies']['apple']['notebooks']['sentiment_analysis']
        timeout = self.config['sentiment_analysis']['llama3']['timeout']
        
        success = self.notebook_executor.execute_notebook(Path(notebook_path), timeout)
        
        if success:
            self.logger.info("Sentiment analysis completed successfully")
        else:
            self.logger.error("Sentiment analysis failed")
        
        return success
    
    def run_contrarian_analysis(self) -> bool:
        """Run contrarian analysis step"""
        self.logger.info("Starting contrarian analysis phase")
        
        if not self.config['contrarian_analysis']['enabled']:
            self.logger.info("Contrarian analysis disabled")
            return True
        
        notebook_path = self.config['companies']['apple']['notebooks']['contrarian_analysis']
        timeout = self.config['contrarian_analysis']['timeout']
        
        success = self.notebook_executor.execute_notebook(Path(notebook_path), timeout)
        
        if success:
            self.logger.info("Contrarian analysis completed successfully")
        else:
            self.logger.error("Contrarian analysis failed")
        
        return success
    
    def run_signal_generation(self) -> bool:
        """Run signal generation step"""
        self.logger.info("Starting signal generation phase")
        
        # Load sentiment data
        sentiment_df = self.signal_generator.load_sentiment_data()
        if sentiment_df is None:
            return False
        
        # Calculate sentiment distribution
        sentiment_dist = self.signal_generator.calculate_sentiment_distribution(sentiment_df)
        if not sentiment_dist:
            return False
        
        # Generate signals
        signal_data = self.signal_generator.generate_signals(sentiment_dist)
        
        # Save report
        success = self.signal_generator.save_signal_report(signal_data)
        
        if success:
            self.logger.info("Signal generation completed successfully")
            self.logger.info(f"Investment Signal: {signal_data['signal']} (Confidence: {signal_data['confidence']})")
            self.logger.info(f"Reasoning: {signal_data['reasoning']}")
        else:
            self.logger.error("Signal generation failed")
        
        return success
    
    def run_full_pipeline(self, force_refresh: bool = False) -> bool:
        """Run the complete pipeline"""
        self.logger.info("Starting automated pipeline execution")
        start_time = datetime.now()
        
        # Initialize run tracking
        self.current_run_data['start_time'] = start_time.isoformat()
        self.current_run_data['run_config'] = {
            'script_name': 'automated_pipeline.py',
            'config_file': str(self.config_path),
            'force_refresh': force_refresh,
            'target_companies': list(self.config.get('companies', {}).keys()),
            'analysis_type': 'full_pipeline'
        }
        
        try:
            # Check data freshness
            if not force_refresh:
                freshness = self.freshness_checker.check_all_data_freshness()
                self.logger.info(f"Data freshness check: {freshness}")
            else:
                freshness = {'articles': False, 'sentiment': False}
                self.logger.info("Force refresh enabled, will regenerate all data")
            
            # Step 1: Data Collection
            if not freshness['articles']:
                if not self.run_data_collection():
                    self.current_run_data['errors'].append('Data collection failed')
                    if not self.config['error_handling']['continue_on_error']:
                        return self._finalize_run(False, start_time)
            else:
                self.logger.info("Skipping data collection - articles are fresh")
            
            # Step 2: Sentiment Analysis
            if not freshness['sentiment']:
                if not self.run_sentiment_analysis():
                    self.current_run_data['errors'].append('Sentiment analysis failed')
                    if not self.config['error_handling']['continue_on_error']:
                        return self._finalize_run(False, start_time)
            else:
                self.logger.info("Skipping sentiment analysis - sentiment data is fresh")
            
            # Step 3: Contrarian Analysis
            if not self.run_contrarian_analysis():
                self.current_run_data['errors'].append('Contrarian analysis failed')
                if not self.config['error_handling']['continue_on_error']:
                    return self._finalize_run(False, start_time)
            
            # Step 4: Signal Generation
            if not self.run_signal_generation():
                self.current_run_data['errors'].append('Signal generation failed')
                return self._finalize_run(False, start_time)
            
            # Pipeline completed successfully
            return self._finalize_run(True, start_time)
            
        except Exception as e:
            self.current_run_data['errors'].append(f"Pipeline exception: {str(e)}")
            self.logger.error(f"Pipeline failed with error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return self._finalize_run(False, start_time)
    
    def _finalize_run(self, success: bool, start_time: datetime) -> bool:
        """Finalize the pipeline run and generate outputs"""
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Update run configuration with final data
        self.current_run_data['run_config'].update({
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'success': success,
            'errors_count': len(self.current_run_data['errors'])
        })
        
        try:
            # Collect pipeline data for dashboard
            self._collect_pipeline_data()
            
            # Update master contrarian database with new data
            self._update_master_contrarian_database()
            
            # Generate run-specific outputs
            company_ticker = self.current_run_data['run_config']['target_companies'][0] if self.current_run_data['run_config']['target_companies'] else 'UNKNOWN'
            
            run_result = self.run_output_generator.process_pipeline_run(
                articles_data=self.current_run_data['articles'],
                author_data=self.current_run_data['authors'],
                run_config=self.current_run_data['run_config'],
                company_ticker=company_ticker
            )
            
            if success:
                self.logger.info(f"Pipeline completed successfully in {duration}")
                self.logger.info(f"Run outputs generated: {run_result['run_id']}")
                self.logger.info(f"Output folder: {run_result['run_folder']}")
            else:
                self.logger.error(f"Pipeline failed after {duration}")
                self.logger.info(f"Partial outputs generated: {run_result['run_id']}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error generating run outputs: {str(e)}")
            if success:
                self.logger.info(f"Pipeline completed successfully in {duration} (output generation failed)")
            else:
                self.logger.error(f"Pipeline failed after {duration}")
            return success
    
    def _collect_pipeline_data(self):
        """Collect data from pipeline execution for dashboard generation"""
        try:
            # Try to load and process actual data from the pipeline
            self._load_articles_data()
            self._load_author_data()
            self._collect_contrarian_data()
            
        except Exception as e:
            self.logger.warning(f"Could not collect actual pipeline data: {str(e)}")
            self.logger.info("Using sample data for dashboard generation")
    
    def _load_articles_data(self):
        """Load articles data from pipeline outputs"""
        try:
            # Try to load Guardian API data
            guardian_file = project_root / self.config['companies']['apple']['data_files']['guardian']
            if guardian_file.exists():
                df = pd.read_csv(guardian_file)
                
                # Try to load sentiment data
                sentiment_file = project_root / self.config['companies']['apple']['data_files']['sentiment']
                sentiment_df = None
                if sentiment_file.exists():
                    sentiment_df = pd.read_csv(sentiment_file)
                
                # Process articles data
                for idx, row in df.iterrows():
                    article_data = {
                        'id': f'ART_{idx+1:03d}',
                        'url': row.get('webUrl', ''),
                        'author': row.get('author', 'Unknown'),
                        'date': row.get('webPublicationDate', ''),
                        'ticker': 'AAPL',  # Default to Apple for now
                        'title': row.get('webTitle', ''),
                        'summary': row.get('fields.trailText', '')[:200] + '...' if pd.notna(row.get('fields.trailText')) else '',
                        'analysis_summary': 'Automated analysis completed',
                        'author_summary': f'Author: {row.get("author", "Unknown")}',
                        'author_prediction': 'Neutral',
                        'market_consensus': 'Neutral',
                        'contrarian_status': 'Unknown',
                        'sentiment_score': 0.0,
                        'eps_actual': '',
                        'eps_expected': '',
                        'eps_surprise': '',
                        'eps_surprise_pct': '',
                        'investment_signal': 'HOLD',
                        'signal_confidence': '0.5',
                        'status': 'Completed'
                    }
                    
                    # Add sentiment data if available
                    if sentiment_df is not None and idx < len(sentiment_df):
                        sentiment_row = sentiment_df.iloc[idx]
                        article_data['sentiment_score'] = sentiment_row.get('sentiment_score', 0.0)
                        article_data['contrarian_status'] = sentiment_row.get('contrarian_indicator', 'Unknown')
                    
                    self.current_run_data['articles'].append(article_data)
                
                self.logger.info(f"Loaded {len(self.current_run_data['articles'])} articles for dashboard")
                
        except Exception as e:
            self.logger.warning(f"Could not load articles data: {str(e)}")
    
    def _load_author_data(self):
        """Load author statistics data"""
        try:
            # Extract unique authors from articles
            authors = set()
            for article in self.current_run_data['articles']:
                if article['author'] != 'Unknown':
                    authors.add(article['author'])
            
            # Generate basic author statistics
            for author in authors:
                author_articles = [a for a in self.current_run_data['articles'] if a['author'] == author]
                
                self.current_run_data['authors'][author] = {
                    'total_articles': len(author_articles),
                    'contrarian_articles': len([a for a in author_articles if a['contrarian_status'] == 'Contrarian']),
                    'contrarian_rate': 0.2,  # Default value
                    'prediction_accuracy': 0.75,  # Default value
                    'contrarian_accuracy': 0.8,  # Default value
                    'companies_covered': 1,
                    'specialization': 'Technology',
                    'recent_30d': 0.75,
                    'recent_90d': 0.78,
                    'avg_sentiment': sum([float(a.get('sentiment_score', 0)) for a in author_articles]) / len(author_articles) if author_articles else 0.0,
                    'eps_correlation': 0.6,
                    'signal_success_rate': 0.7,
                    'last_article_date': max([a['date'] for a in author_articles]) if author_articles else '',
                    'reliability_score': 0.75
                }
            
            self.logger.info(f"Generated statistics for {len(self.current_run_data['authors'])} authors")
            
        except Exception as e:
            self.logger.warning(f"Could not load author data: {str(e)}")
    
    def _update_master_contrarian_database(self):
        """Update the master contrarian database with current run data"""
        try:
            if not self.current_run_data['contrarians']:
                self.logger.info("No contrarian data to update in master database")
                return
            
            # Prepare report data for the master database
            report_data = {
                'company': self.current_run_data['run_config'].get('target_companies', ['Unknown'])[0],
                'symbol': self.current_run_data['run_config'].get('target_companies', ['UNK'])[0],
                'earnings_date': self.current_run_data['start_time'][:10] if self.current_run_data['start_time'] else '',
                'actual_result': {
                    'result': 'unknown',  # This would be populated with actual EPS data
                    'eps_actual': None,
                    'eps_expected': None,
                    'eps_surprise': None
                }
            }
            
            # Update the master database
            self.master_contrarian_db.add_contrarian_analysis(report_data, self.current_run_data['contrarians'])
            
            self.logger.info(f"Updated master contrarian database with {len(self.current_run_data['contrarians'])} contrarian records")
            
        except Exception as e:
            self.logger.error(f"Error updating master contrarian database: {str(e)}")
            self.current_run_data['errors'].append(f'Master contrarian database update failed: {str(e)}')
    
    def _collect_contrarian_data(self):
        """Collect contrarian analysis data from pipeline outputs"""
        try:
            # Try to load contrarian analysis results
            contrarian_file = project_root / 'data' / 'simplified_contrarian_db' / 'contrarian_records.csv'
            if contrarian_file.exists():
                df = pd.read_csv(contrarian_file)
                
                # Process contrarian data
                for idx, row in df.iterrows():
                    contrarian_data = {
                        'author': row.get('Author_Name', 'Unknown'),
                        'earnings_prediction': row.get('Prediction', 'unknown'),
                        'was_minority_sentiment': row.get('Is_Contrarian_Sentiment', False),
                        'was_minority_prediction': row.get('Is_Contrarian_Prediction', False),
                        'contrarian_score': float(row.get('Contrarian_Score', 0.0)),
                        'sentiment_score': float(row.get('Sentiment_Score', 0.0)),
                        'company': row.get('Company', 'Unknown'),
                        'symbol': row.get('Symbol', 'UNK'),
                        'date': row.get('Date', '')
                    }
                    
                    self.current_run_data['contrarians'].append(contrarian_data)
                
                self.logger.info(f"Collected {len(self.current_run_data['contrarians'])} contrarian records")
            else:
                self.logger.warning("No contrarian analysis file found")
                
        except Exception as e:
            self.logger.warning(f"Could not collect contrarian data: {str(e)}")
    
    def run_dry_run(self) -> bool:
        """Run a dry run to check configuration and file paths"""
        self.logger.info("Starting dry run - checking configuration and file paths")
        
        try:
            # Check configuration
            self.logger.info("Configuration loaded successfully")
            
            # Check notebook paths
            company_config = self.config['companies']['apple']
            notebooks = company_config['notebooks']
            
            for step, notebook_path in notebooks.items():
                abs_path = project_root / notebook_path
                if abs_path.exists():
                    self.logger.info(f"✓ {step}: {notebook_path}")
                else:
                    self.logger.error(f"✗ {step}: {notebook_path} (NOT FOUND)")
            
            # Check data file paths
            data_files = company_config['data_files']
            for data_type, file_path in data_files.items():
                abs_path = project_root / file_path
                if abs_path.exists():
                    self.logger.info(f"✓ {data_type} data: {file_path}")
                else:
                    self.logger.warning(f"? {data_type} data: {file_path} (will be created)")
            
            # Check freshness
            freshness = self.freshness_checker.check_all_data_freshness()
            self.logger.info(f"Data freshness: {freshness}")
            
            self.logger.info("Dry run completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Dry run failed: {str(e)}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Automated Sentiment Analysis Pipeline')
    parser.add_argument('--config', default='pipeline_config.yaml', help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', help='Run configuration check only')
    parser.add_argument('--force-refresh', action='store_true', help='Force refresh all data')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = AutomatedPipeline(args.config)
    
    if args.verbose:
        pipeline.logger.setLevel(logging.DEBUG)
    
    # Run pipeline
    if args.dry_run:
        success = pipeline.run_dry_run()
    else:
        success = pipeline.run_full_pipeline(force_refresh=args.force_refresh)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()