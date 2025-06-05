#!/usr/bin/env python3
"""
Run Output Generator - Automated Dashboard Creation

This module automatically creates run-specific output folders and CSV files
whenever the pipeline runs, providing detailed analysis dashboards.

Features:
- Automatic run ID generation
- Run-specific folder creation
- Articles summary dashboard CSV
- Author statistics CSV
- Run metadata tracking
"""

import os
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

class RunOutputGenerator:
    """Generates run-specific output folders and dashboard CSV files"""
    
    def __init__(self, base_output_dir: str = None):
        """
        Initialize the run output generator
        
        Args:
            base_output_dir: Base directory for run outputs (defaults to data/run_outputs)
        """
        if base_output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.base_output_dir = project_root / "data" / "run_outputs"
        else:
            self.base_output_dir = Path(base_output_dir)
        
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def generate_run_id(self) -> str:
        """
        Generate a unique run ID based on timestamp
        
        Returns:
            Unique run ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"RUN_{timestamp}"
    
    def create_run_folder(self, run_id: str) -> Path:
        """
        Create a new run-specific folder
        
        Args:
            run_id: Unique run identifier
            
        Returns:
            Path to the created run folder
        """
        run_folder = self.base_output_dir / run_id
        run_folder.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Created run folder: {run_folder}")
        return run_folder
    
    def create_articles_dashboard(self, run_folder: Path, articles_data: List[Dict]) -> Path:
        """
        Create articles summary dashboard CSV
        
        Args:
            run_folder: Path to the run folder
            articles_data: List of article analysis data
            
        Returns:
            Path to the created CSV file
        """
        csv_file = run_folder / "articles_summary_dashboard.csv"
        
        # Define CSV headers
        headers = [
            'Article_ID', 'Article_Link', 'Author', 'Publication_Date', 'Company_Ticker',
            'Article_Title', 'Article_Summary', 'Analysis_Summary', 'Author_Summary',
            'Author_Prediction', 'Market_Consensus', 'Contrarian_Status', 'Sentiment_Score',
            'EPS_Actual', 'EPS_Expected', 'EPS_Surprise', 'EPS_Surprise_Percentage',
            'Investment_Signal', 'Signal_Confidence', 'Processing_Status'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for i, article in enumerate(articles_data, 1):
                row = {
                    'Article_ID': article.get('id', f'ART_{i:03d}'),
                    'Article_Link': article.get('url', ''),
                    'Author': article.get('author', 'Unknown'),
                    'Publication_Date': article.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'Company_Ticker': article.get('ticker', ''),
                    'Article_Title': article.get('title', ''),
                    'Article_Summary': article.get('summary', ''),
                    'Analysis_Summary': article.get('analysis_summary', ''),
                    'Author_Summary': article.get('author_summary', ''),
                    'Author_Prediction': article.get('author_prediction', ''),
                    'Market_Consensus': article.get('market_consensus', ''),
                    'Contrarian_Status': article.get('contrarian_status', 'Unknown'),
                    'Sentiment_Score': article.get('sentiment_score', 0.0),
                    'EPS_Actual': article.get('eps_actual', ''),
                    'EPS_Expected': article.get('eps_expected', ''),
                    'EPS_Surprise': article.get('eps_surprise', ''),
                    'EPS_Surprise_Percentage': article.get('eps_surprise_pct', ''),
                    'Investment_Signal': article.get('investment_signal', ''),
                    'Signal_Confidence': article.get('signal_confidence', ''),
                    'Processing_Status': article.get('status', 'Completed')
                }
                writer.writerow(row)
        
        self.logger.info(f"Created articles dashboard: {csv_file}")
        return csv_file
    
    def create_author_statistics(self, run_folder: Path, author_data: Dict[str, Dict]) -> Path:
        """
        Create author statistics CSV
        
        Args:
            run_folder: Path to the run folder
            author_data: Dictionary of author statistics
            
        Returns:
            Path to the created CSV file
        """
        csv_file = run_folder / "author_statistics.csv"
        
        # Define CSV headers
        headers = [
            'Author_Name', 'Total_Articles', 'Contrarian_Articles', 'Contrarian_Rate',
            'Prediction_Accuracy', 'Contrarian_Accuracy', 'Companies_Covered',
            'Primary_Specialization', 'Recent_Performance_30d', 'Recent_Performance_90d',
            'Average_Sentiment_Score', 'EPS_Surprise_Correlation', 'Signal_Success_Rate',
            'Last_Article_Date', 'Author_Reliability_Score'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for author_name, stats in author_data.items():
                row = {
                    'Author_Name': author_name,
                    'Total_Articles': stats.get('total_articles', 0),
                    'Contrarian_Articles': stats.get('contrarian_articles', 0),
                    'Contrarian_Rate': stats.get('contrarian_rate', 0.0),
                    'Prediction_Accuracy': stats.get('prediction_accuracy', 0.0),
                    'Contrarian_Accuracy': stats.get('contrarian_accuracy', 0.0),
                    'Companies_Covered': stats.get('companies_covered', 0),
                    'Primary_Specialization': stats.get('specialization', ''),
                    'Recent_Performance_30d': stats.get('recent_30d', 0.0),
                    'Recent_Performance_90d': stats.get('recent_90d', 0.0),
                    'Average_Sentiment_Score': stats.get('avg_sentiment', 0.0),
                    'EPS_Surprise_Correlation': stats.get('eps_correlation', 0.0),
                    'Signal_Success_Rate': stats.get('signal_success_rate', 0.0),
                    'Last_Article_Date': stats.get('last_article_date', ''),
                    'Author_Reliability_Score': stats.get('reliability_score', 0.0)
                }
                writer.writerow(row)
        
        self.logger.info(f"Created author statistics: {csv_file}")
        return csv_file
    
    def create_run_metadata(self, run_folder: Path, run_config: Dict) -> Path:
        """
        Create run metadata JSON file
        
        Args:
            run_folder: Path to the run folder
            run_config: Run configuration and metadata
            
        Returns:
            Path to the created JSON file
        """
        metadata_file = run_folder / "run_metadata.json"
        
        metadata = {
            'run_id': run_config.get('run_id'),
            'start_time': run_config.get('start_time'),
            'end_time': run_config.get('end_time'),
            'duration_seconds': run_config.get('duration_seconds'),
            'script_name': run_config.get('script_name', 'automated_pipeline.py'),
            'config_file': run_config.get('config_file'),
            'target_companies': run_config.get('target_companies', []),
            'analysis_type': run_config.get('analysis_type', 'full_pipeline'),
            'total_articles_processed': run_config.get('total_articles', 0),
            'contrarians_identified': run_config.get('contrarians_found', 0),
            'success_rate': run_config.get('success_rate', 0.0),
            'errors_encountered': run_config.get('errors', []),
            'output_files': run_config.get('output_files', []),
            'pipeline_version': run_config.get('version', '1.0'),
            'system_info': {
                'python_version': run_config.get('python_version'),
                'platform': run_config.get('platform'),
                'memory_usage_mb': run_config.get('memory_usage'),
                'cpu_usage_percent': run_config.get('cpu_usage')
            }
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        self.logger.info(f"Created run metadata: {metadata_file}")
        return metadata_file
    
    def generate_sample_data(self, run_folder: Path, company_ticker: str = "AAPL") -> Dict[str, Path]:
        """
        Generate sample data for testing purposes
        
        Args:
            run_folder: Path to the run folder
            company_ticker: Company ticker symbol
            
        Returns:
            Dictionary of created file paths
        """
        # Sample articles data
        sample_articles = [
            {
                'id': 'ART_001',
                'url': 'https://example.com/article1',
                'author': 'John Smith',
                'date': '2024-01-15',
                'ticker': company_ticker,
                'title': f'{company_ticker} Earnings Preview: Challenges Ahead',
                'summary': 'Article discusses potential challenges for upcoming earnings',
                'analysis_summary': 'Bearish sentiment with concerns about revenue growth',
                'author_summary': 'Historically accurate analyst with tech focus',
                'author_prediction': 'Negative',
                'market_consensus': 'Positive',
                'contrarian_status': 'Contrarian',
                'sentiment_score': -0.3,
                'eps_actual': '1.85',
                'eps_expected': '1.90',
                'eps_surprise': '-0.05',
                'eps_surprise_pct': '-2.6%',
                'investment_signal': 'SELL',
                'signal_confidence': '0.75',
                'status': 'Completed'
            },
            {
                'id': 'ART_002',
                'url': 'https://example.com/article2',
                'author': 'Sarah Johnson',
                'date': '2024-01-16',
                'ticker': company_ticker,
                'title': f'{company_ticker} Innovation Drive Continues',
                'summary': 'Positive outlook on company innovation and market position',
                'analysis_summary': 'Bullish sentiment highlighting growth opportunities',
                'author_summary': 'Emerging analyst with strong track record',
                'author_prediction': 'Positive',
                'market_consensus': 'Negative',
                'contrarian_status': 'Contrarian',
                'sentiment_score': 0.6,
                'eps_actual': '2.10',
                'eps_expected': '1.95',
                'eps_surprise': '0.15',
                'eps_surprise_pct': '7.7%',
                'investment_signal': 'BUY',
                'signal_confidence': '0.82',
                'status': 'Completed'
            }
        ]
        
        # Sample author data
        sample_authors = {
            'John Smith': {
                'total_articles': 45,
                'contrarian_articles': 12,
                'contrarian_rate': 0.267,
                'prediction_accuracy': 0.78,
                'contrarian_accuracy': 0.83,
                'companies_covered': 8,
                'specialization': 'Technology',
                'recent_30d': 0.75,
                'recent_90d': 0.79,
                'avg_sentiment': -0.15,
                'eps_correlation': 0.65,
                'signal_success_rate': 0.71,
                'last_article_date': '2024-01-15',
                'reliability_score': 0.76
            },
            'Sarah Johnson': {
                'total_articles': 23,
                'contrarian_articles': 8,
                'contrarian_rate': 0.348,
                'prediction_accuracy': 0.82,
                'contrarian_accuracy': 0.88,
                'companies_covered': 5,
                'specialization': 'Growth Stocks',
                'recent_30d': 0.85,
                'recent_90d': 0.81,
                'avg_sentiment': 0.25,
                'eps_correlation': 0.72,
                'signal_success_rate': 0.79,
                'last_article_date': '2024-01-16',
                'reliability_score': 0.83
            }
        }
        
        # Sample run config
        sample_config = {
            'run_id': run_folder.name,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now()).isoformat(),
            'duration_seconds': 125,
            'script_name': 'automated_pipeline.py',
            'config_file': 'pipeline_config.yaml',
            'target_companies': [company_ticker],
            'analysis_type': 'full_pipeline',
            'total_articles': len(sample_articles),
            'contrarians_found': 2,
            'success_rate': 1.0,
            'errors': [],
            'output_files': ['articles_summary_dashboard.csv', 'author_statistics.csv'],
            'version': '1.0',
            'python_version': '3.9.0',
            'platform': 'macOS',
            'memory_usage': 256,
            'cpu_usage': 15.2
        }
        
        # Create files
        created_files = {
            'articles_dashboard': self.create_articles_dashboard(run_folder, sample_articles),
            'author_statistics': self.create_author_statistics(run_folder, sample_authors),
            'run_metadata': self.create_run_metadata(run_folder, sample_config)
        }
        
        return created_files
    
    def process_pipeline_run(self, articles_data: List[Dict] = None, 
                           author_data: Dict[str, Dict] = None,
                           run_config: Dict = None,
                           company_ticker: str = "AAPL") -> Dict[str, Any]:
        """
        Main method to process a complete pipeline run
        
        Args:
            articles_data: List of article analysis data
            author_data: Dictionary of author statistics
            run_config: Run configuration and metadata
            company_ticker: Company ticker symbol
            
        Returns:
            Dictionary with run information and created file paths
        """
        # Generate run ID and create folder
        run_id = self.generate_run_id()
        run_folder = self.create_run_folder(run_id)
        
        # If no data provided, generate sample data
        if articles_data is None or author_data is None:
            self.logger.info("No data provided, generating sample data")
            created_files = self.generate_sample_data(run_folder, company_ticker)
        else:
            # Create files with provided data
            created_files = {
                'articles_dashboard': self.create_articles_dashboard(run_folder, articles_data),
                'author_statistics': self.create_author_statistics(run_folder, author_data)
            }
            
            if run_config:
                created_files['run_metadata'] = self.create_run_metadata(run_folder, run_config)
        
        result = {
            'run_id': run_id,
            'run_folder': run_folder,
            'created_files': created_files,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"Pipeline run output generated: {run_id}")
        return result

# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create generator
    generator = RunOutputGenerator()
    
    # Process a sample run
    result = generator.process_pipeline_run(company_ticker="AAPL")
    
    print(f"Generated run: {result['run_id']}")
    print(f"Run folder: {result['run_folder']}")
    print("Created files:")
    for file_type, file_path in result['created_files'].items():
        print(f"  - {file_type}: {file_path}")