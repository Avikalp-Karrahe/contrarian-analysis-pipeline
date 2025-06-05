#!/usr/bin/env python3
"""
Contrarian CSV Exporter

This module handles exporting contrarian analysis results to various CSV formats
for further analysis and reporting.
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from .master_contrarian_database import MasterContrarianDatabase

class ContrarianCSVExporter:
    """
    Exports contrarian analysis data to CSV format for easy monitoring and analysis
    """
    
    def __init__(self, output_dir: str = "outputs", create_run_folder: bool = False):
        # Get the project root directory (two levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Use absolute path relative to project root
        if not os.path.isabs(output_dir):
            self.output_dir = os.path.join(project_root, output_dir)
            self.base_output_dir = self.output_dir
        else:
            self.output_dir = output_dir
            self.base_output_dir = output_dir
            
        self.create_run_folder = create_run_folder
        self.run_folder = None
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize master contrarian database
        self.master_db = MasterContrarianDatabase()
    
    def _get_run_folder(self, symbol: str) -> str:
        """
        Create or get the run-specific folder for this analysis
        """
        if not self.create_run_folder:
            return self.base_output_dir
            
        if self.run_folder is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.run_folder = os.path.join(self.base_output_dir, f"{symbol}_{timestamp}")
            os.makedirs(self.run_folder, exist_ok=True)
            print(f"Created analysis run folder: {self.run_folder}")
        
        return self.run_folder
    
    def export_articles_analysis(self, analyzed_articles: List[Dict], 
                               company: str, symbol: str, 
                               earnings_date: str) -> str:
        """
        Export analyzed articles to CSV with detailed information
        """
        output_dir = self._get_run_folder(symbol)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"articles_analysis_{symbol}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Define CSV headers
        headers = [
            'Company',
            'Symbol', 
            'Earnings_Date',
            'Article_Date',
            'Author',
            'Headline',
            'Section',
            'Word_Count',
            'URL',
            'Sentiment',
            'Sentiment_Confidence',
            'Earnings_Prediction',
            'Prediction_Confidence',
            'Key_Concerns',
            'Reasoning',
            'Analysis_Success',
            'Analysis_Date'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for article in analyzed_articles:
                analysis = article.get('analysis') or {}
                
                # Handle key concerns (convert list to string)
                key_concerns = analysis.get('key_concerns', [])
                if isinstance(key_concerns, list):
                    key_concerns_str = '; '.join(key_concerns)
                else:
                    key_concerns_str = str(key_concerns) if key_concerns else ''
                
                row = {
                    'Company': company,
                    'Symbol': symbol,
                    'Earnings_Date': earnings_date,
                    'Article_Date': article.get('date', ''),
                    'Author': article.get('author', 'Unknown'),
                    'Headline': article.get('headline', ''),
                    'Section': article.get('section', ''),
                    'Word_Count': article.get('word_count', 0),
                    'URL': article.get('url', ''),
                    'Sentiment': analysis.get('sentiment', 'N/A'),
                    'Sentiment_Confidence': analysis.get('confidence', 'N/A'),
                    'Earnings_Prediction': analysis.get('earnings_prediction', 'N/A'),
                    'Prediction_Confidence': analysis.get('prediction_confidence', 'N/A'),
                    'Key_Concerns': key_concerns_str,
                    'Reasoning': analysis.get('reasoning', ''),
                    'Analysis_Success': 'Yes' if analysis else 'No',
                    'Analysis_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                writer.writerow(row)
        
        print(f"Articles analysis exported to: {filepath}")
        return filepath
    
    def export_contrarians_summary(self, contrarians: List[Dict], 
                                 sentiment_dist: Dict, prediction_dist: Dict,
                                 company: str, symbol: str, 
                                 earnings_date: str, actual_result: Dict = None) -> str:
        """
        Export contrarian analysts summary to CSV
        """
        output_dir = self._get_run_folder(symbol)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contrarians_summary_{symbol}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        headers = [
            'Company',
            'Symbol',
            'Earnings_Date',
            'Rank',
            'Author',
            'Headline',
            'Article_Date',
            'Sentiment',
            'Prediction',
            'Sentiment_Percentage',
            'Prediction_Percentage',
            'Was_Minority_Sentiment',
            'Was_Minority_Prediction',
            'Sentiment_Correct',
            'Prediction_Correct',
            'Contrarian_Score',
            'Confidence',
            'Prediction_Confidence',
            'Reasoning',
            'URL'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for i, contrarian in enumerate(contrarians, 1):
                row = {
                    'Company': company,
                    'Symbol': symbol,
                    'Earnings_Date': earnings_date,
                    'Rank': i,
                    'Author': contrarian.get('author', 'Unknown'),
                    'Headline': contrarian.get('headline', ''),
                    'Article_Date': contrarian.get('date', ''),
                    'Sentiment': contrarian.get('sentiment', ''),
                    'Prediction': contrarian.get('prediction', ''),
                    'Sentiment_Percentage': contrarian.get('sentiment_percentage', 0),
                    'Prediction_Percentage': contrarian.get('prediction_percentage', 0),
                    'Was_Minority_Sentiment': contrarian.get('was_minority_sentiment', False),
                    'Was_Minority_Prediction': contrarian.get('was_minority_prediction', False),
                    'Sentiment_Correct': contrarian.get('sentiment_correct', False),
                    'Prediction_Correct': contrarian.get('prediction_correct', False),
                    'Contrarian_Score': contrarian.get('contrarian_score', 0),
                    'Confidence': contrarian.get('confidence', ''),
                    'Prediction_Confidence': contrarian.get('prediction_confidence', ''),
                    'Reasoning': contrarian.get('reasoning', ''),
                    'URL': contrarian.get('url', '')
                }
                
                writer.writerow(row)
        
        print(f"Contrarians summary exported to: {filepath}")
        return filepath
    
    def export_market_consensus(self, sentiment_dist: Dict, prediction_dist: Dict,
                              company: str, symbol: str, earnings_date: str,
                              total_articles: int, actual_result: Dict = None) -> str:
        """
        Export market consensus data to CSV
        """
        output_dir = self._get_run_folder(symbol)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"market_consensus_{symbol}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        headers = [
            'Company',
            'Symbol',
            'Earnings_Date',
            'Analysis_Date',
            'Total_Articles',
            'Metric_Type',
            'Category',
            'Count',
            'Percentage',
            'Is_Majority'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            analysis_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Export sentiment distribution
            max_sentiment_count = max(sentiment_dist.values()) if sentiment_dist else 0
            for sentiment, count in sentiment_dist.items():
                percentage = (count / total_articles * 100) if total_articles > 0 else 0
                row = {
                    'Company': company,
                    'Symbol': symbol,
                    'Earnings_Date': earnings_date,
                    'Analysis_Date': analysis_date,
                    'Total_Articles': total_articles,
                    'Metric_Type': 'Sentiment',
                    'Category': sentiment,
                    'Count': count,
                    'Percentage': round(percentage, 1),
                    'Is_Majority': count == max_sentiment_count
                }
                writer.writerow(row)
            
            # Export prediction distribution
            max_prediction_count = max(prediction_dist.values()) if prediction_dist else 0
            for prediction, count in prediction_dist.items():
                percentage = (count / total_articles * 100) if total_articles > 0 else 0
                row = {
                    'Company': company,
                    'Symbol': symbol,
                    'Earnings_Date': earnings_date,
                    'Analysis_Date': analysis_date,
                    'Total_Articles': total_articles,
                    'Metric_Type': 'Prediction',
                    'Category': prediction,
                    'Count': count,
                    'Percentage': round(percentage, 1),
                    'Is_Majority': count == max_prediction_count
                }
                writer.writerow(row)
        
        print(f"Market consensus exported to: {filepath}")
        return filepath
    
    def export_articles_summary(self, analyzed_articles: List[Dict], 
                              company: str, symbol: str, 
                              earnings_date: str) -> str:
        """
        Export a simplified articles summary with title, author, and link
        """
        output_dir = self._get_run_folder(symbol)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"articles_summary_{symbol}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        headers = [
            'Company',
            'Symbol',
            'Earnings_Date',
            'Article_Date',
            'Author',
            'Article_Title',
            'Article_URL',
            'Sentiment',
            'Earnings_Prediction',
            'Analysis_Date'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for article in analyzed_articles:
                analysis = article.get('analysis') or {}
                
                row = {
                    'Company': company,
                    'Symbol': symbol,
                    'Earnings_Date': earnings_date,
                    'Article_Date': article.get('date', ''),
                    'Author': article.get('author', 'Unknown'),
                    'Article_Title': article.get('headline', ''),
                    'Article_URL': article.get('url', ''),
                    'Sentiment': analysis.get('sentiment', 'N/A'),
                    'Earnings_Prediction': analysis.get('earnings_prediction', 'N/A'),
                    'Analysis_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                writer.writerow(row)
        
        print(f"Articles summary exported to: {filepath}")
        return filepath
    
    def export_author_contrarian_tracker(self, analyzed_articles: List[Dict], 
                                        contrarians: List[Dict],
                                        sentiment_dist: Dict, prediction_dist: Dict,
                                        company: str, symbol: str, 
                                        earnings_date: str) -> str:
        """
        Export author-focused contrarian detection data to CSV for easier tracking
        """
        output_dir = self._get_run_folder(symbol)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"author_contrarian_tracker_{symbol}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # Calculate author statistics
        author_stats = {}
        
        # Get majority sentiment and prediction
        majority_sentiment = max(sentiment_dist, key=sentiment_dist.get) if sentiment_dist else None
        majority_prediction = max(prediction_dist, key=prediction_dist.get) if prediction_dist else None
        
        # Process all analyzed articles
        for article in analyzed_articles:
            author = article.get('author', 'Unknown')
            analysis = article.get('analysis') or {}
            sentiment = analysis.get('sentiment', 'N/A')
            prediction = analysis.get('earnings_prediction', 'N/A')
            
            if author not in author_stats:
                author_stats[author] = {
                    'total_articles': 0,
                    'contrarian_sentiment_count': 0,
                    'contrarian_prediction_count': 0,
                    'sentiment_breakdown': {},
                    'prediction_breakdown': {},
                    'is_identified_contrarian': False,
                    'contrarian_rank': None,
                    'contrarian_score': 0,
                    'latest_article_date': '',
                    'latest_headline': '',
                    'latest_url': ''
                }
            
            stats = author_stats[author]
            stats['total_articles'] += 1
            
            # Track sentiment breakdown
            if sentiment not in stats['sentiment_breakdown']:
                stats['sentiment_breakdown'][sentiment] = 0
            stats['sentiment_breakdown'][sentiment] += 1
            
            # Track prediction breakdown
            if prediction not in stats['prediction_breakdown']:
                stats['prediction_breakdown'][prediction] = 0
            stats['prediction_breakdown'][prediction] += 1
            
            # Check if contrarian
            if sentiment != majority_sentiment and sentiment != 'N/A':
                stats['contrarian_sentiment_count'] += 1
            if prediction != majority_prediction and prediction != 'N/A':
                stats['contrarian_prediction_count'] += 1
            
            # Update latest article info
            article_date = article.get('date', '')
            if article_date > stats['latest_article_date']:
                stats['latest_article_date'] = article_date
                stats['latest_headline'] = article.get('headline', '')
                stats['latest_url'] = article.get('url', '')
        
        # Mark identified contrarians
        if contrarians:
            for i, contrarian in enumerate(contrarians, 1):
                author = contrarian.get('author', 'Unknown')
                if author in author_stats:
                    author_stats[author]['is_identified_contrarian'] = True
                    author_stats[author]['contrarian_rank'] = i
                    author_stats[author]['contrarian_score'] = contrarian.get('contrarian_score', 0)
        
        # Define CSV headers
        headers = [
            'Company',
            'Symbol',
            'Earnings_Date',
            'Author',
            'Total_Articles',
            'Contrarian_Sentiment_Count',
            'Contrarian_Prediction_Count',
            'Contrarian_Sentiment_Rate',
            'Contrarian_Prediction_Rate',
            'Overall_Contrarian_Rate',
            'Is_Identified_Contrarian',
            'Contrarian_Rank',
            'Contrarian_Score',
            'Dominant_Sentiment',
            'Dominant_Prediction',
            'Sentiment_Diversity_Score',
            'Latest_Article_Date',
            'Latest_Headline',
            'Latest_URL',
            'Analysis_Date'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for author, stats in author_stats.items():
                # Calculate rates
                sentiment_rate = (stats['contrarian_sentiment_count'] / stats['total_articles'] * 100) if stats['total_articles'] > 0 else 0
                prediction_rate = (stats['contrarian_prediction_count'] / stats['total_articles'] * 100) if stats['total_articles'] > 0 else 0
                overall_rate = ((stats['contrarian_sentiment_count'] + stats['contrarian_prediction_count']) / (stats['total_articles'] * 2) * 100) if stats['total_articles'] > 0 else 0
                
                # Find dominant sentiment and prediction
                dominant_sentiment = max(stats['sentiment_breakdown'], key=stats['sentiment_breakdown'].get) if stats['sentiment_breakdown'] else 'N/A'
                dominant_prediction = max(stats['prediction_breakdown'], key=stats['prediction_breakdown'].get) if stats['prediction_breakdown'] else 'N/A'
                
                # Calculate diversity score (how varied their opinions are)
                sentiment_diversity = len(stats['sentiment_breakdown'])
                prediction_diversity = len(stats['prediction_breakdown'])
                diversity_score = (sentiment_diversity + prediction_diversity) / 2
                
                row = {
                    'Company': company,
                    'Symbol': symbol,
                    'Earnings_Date': earnings_date,
                    'Author': author,
                    'Total_Articles': stats['total_articles'],
                    'Contrarian_Sentiment_Count': stats['contrarian_sentiment_count'],
                    'Contrarian_Prediction_Count': stats['contrarian_prediction_count'],
                    'Contrarian_Sentiment_Rate': round(sentiment_rate, 1),
                    'Contrarian_Prediction_Rate': round(prediction_rate, 1),
                    'Overall_Contrarian_Rate': round(overall_rate, 1),
                    'Is_Identified_Contrarian': stats['is_identified_contrarian'],
                    'Contrarian_Rank': stats['contrarian_rank'] or '',
                    'Contrarian_Score': stats['contrarian_score'],
                    'Dominant_Sentiment': dominant_sentiment,
                    'Dominant_Prediction': dominant_prediction,
                    'Sentiment_Diversity_Score': round(diversity_score, 1),
                    'Latest_Article_Date': stats['latest_article_date'],
                    'Latest_Headline': stats['latest_headline'],
                    'Latest_URL': stats['latest_url'],
                    'Analysis_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                writer.writerow(row)
        
        print(f"Author contrarian tracker exported to: {filepath}")
        return filepath
    
    def update_master_contrarian_database(self, report_data: Dict[str, Any]):
        """
        Update the master contrarian database with new analysis results
        """
        try:
            contrarians = report_data.get('contrarian_analysts', [])
            if contrarians:
                print(f"\nUpdating master contrarian database with {len(contrarians)} contrarian(s)...")
                self.master_db.add_contrarian_analysis(report_data, contrarians)
                print("Master contrarian database updated successfully!")
            else:
                print("\nNo contrarians found in this analysis - master database not updated.")
        except Exception as e:
            print(f"Error updating master contrarian database: {e}")
    
    def get_master_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics from the master contrarian database
        """
        try:
            import pandas as pd
            
            if os.path.exists(self.master_db.master_csv_path):
                df = pd.read_csv(self.master_db.master_csv_path)
                
                stats = {
                    'total_authors': len(df),
                    'total_contrarian_instances': df['Total_Contrarian_Instances'].sum(),
                    'repeat_contrarians': len(df[df['Total_Contrarian_Instances'] > 1]),
                    'avg_success_rate': df['Contrarian_Success_Rate'].mean(),
                    'top_performer': df.loc[df['Contrarian_Success_Rate'].idxmax(), 'Author_Name'] if not df.empty else None,
                    'most_active': df.loc[df['Total_Contrarian_Instances'].idxmax(), 'Author_Name'] if not df.empty else None
                }
                
                return stats
            else:
                return {'error': 'Master database not found'}
        except Exception as e:
            return {'error': f'Error reading master database: {e}'}
    
    def export_master_database_summary(self, output_folder: str = None) -> str:
        """
        Export a summary of the master contrarian database
        """
        if output_folder is None:
            output_folder = self.output_dir
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = os.path.join(output_folder, f'master_database_summary_{timestamp}.csv')
        
        try:
            import pandas as pd
            
            if os.path.exists(self.master_db.master_csv_path):
                # Copy the master database to the output folder
                df = pd.read_csv(self.master_db.master_csv_path)
                df.to_csv(csv_path, index=False)
                
                print(f"Master database summary exported: {csv_path}")
                return csv_path
            else:
                print("Master database not found - cannot export summary")
                return None
        except Exception as e:
            print(f"Error exporting master database summary: {e}")
            return None

    def export_full_analysis(self, report_data: Dict) -> Dict[str, str]:
        """
        Export complete analysis to multiple CSV files
        """
        company = report_data.get('company', 'Unknown')
        symbol = report_data.get('symbol', 'UNK')
        earnings_date = report_data.get('earnings_date', '')
        
        # Get data from report
        analyzed_articles = report_data.get('analyzed_articles', [])
        contrarians = report_data.get('contrarian_analysts', [])
        summary = report_data.get('summary') or {}
        sentiment_dist = summary.get('sentiment_distribution', {})
        prediction_dist = summary.get('prediction_distribution', {})
        actual_result = report_data.get('actual_result')
        data_collection = report_data.get('data_collection') or {}
        total_articles = data_collection.get('articles_analyzed', 0)
        
        exported_files = {}
        
        # Export articles analysis
        if analyzed_articles:
            exported_files['articles'] = self.export_articles_analysis(
                analyzed_articles, company, symbol, earnings_date
            )
            # Export simplified articles summary
            exported_files['articles_summary'] = self.export_articles_summary(
                analyzed_articles, company, symbol, earnings_date
            )
            # Export author contrarian tracker
            exported_files['author_tracker'] = self.export_author_contrarian_tracker(
                analyzed_articles, contrarians, sentiment_dist, prediction_dist,
                company, symbol, earnings_date
            )
        
        # Export contrarians summary
        if contrarians:
            exported_files['contrarians'] = self.export_contrarians_summary(
                contrarians, sentiment_dist, prediction_dist, 
                company, symbol, earnings_date, actual_result
            )
        
        # Export market consensus
        exported_files['consensus'] = self.export_market_consensus(
            sentiment_dist, prediction_dist, company, symbol, 
            earnings_date, total_articles, actual_result
        )
        
        # Update master contrarian database
        self.update_master_contrarian_database(report_data)
        
        return exported_files
    
    def load_and_export_json_report(self, json_filepath: str) -> Dict[str, str]:
        """
        Load a JSON report and export to CSV files
        """
        try:
            with open(json_filepath, 'r') as f:
                report_data = json.load(f)
            
            print(f"Loading report from: {json_filepath}")
            return self.export_full_analysis(report_data)
            
        except Exception as e:
            print(f"Error loading JSON report: {e}")
            return {}

def main():
    """
    Example usage of the CSV exporter
    """
    exporter = ContrarianCSVExporter()
    
    # Example: Export existing JSON reports to CSV
    # Get the project root directory (two levels up from this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    reports_dir = os.path.join(project_root, "outputs")
    
    if os.path.exists(reports_dir):
        json_files = [f for f in os.listdir(reports_dir) if f.endswith('.json') and 'contrarian' in f]
        
        print(f"Found {len(json_files)} contrarian JSON reports to convert:")
        
        for json_file in json_files:
            json_path = os.path.join(reports_dir, json_file)
            print(f"\nConverting: {json_file}")
            
            exported_files = exporter.load_and_export_json_report(json_path)
            
            if exported_files:
                print("Exported CSV files:")
                for file_type, filepath in exported_files.items():
                    print(f"  {file_type}: {filepath}")
            else:
                print("  No CSV files exported (possibly no data)")
    
    else:
        print(f"Reports directory not found at: {reports_dir}")
        print("Run a contrarian analysis first to generate reports.")

if __name__ == "__main__":
    main()