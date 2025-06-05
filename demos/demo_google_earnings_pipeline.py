#!/usr/bin/env python3
"""
Google Earnings Pipeline Test

This script tests the full simplified contrarian analysis pipeline for 4 Google earnings calls.
It demonstrates how the system:
1. Identifies contrarian analysts across multiple earnings periods
2. Tracks their accuracy over time
3. Builds historical performance records
4. Provides investment signals based on contrarian consensus
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import pandas as pd

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simplified_contrarian_analyzer import SimplifiedContrarianAnalyzer

def setup_logging():
    """Setup logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('google_earnings_pipeline.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def test_google_earnings_pipeline():
    """Test the full pipeline with 4 Google earnings calls"""
    logger = setup_logging()
    logger.info("Starting Google Earnings Pipeline Test")
    
    # Initialize the simplified contrarian analyzer
    analyzer = SimplifiedContrarianAnalyzer()
    
    # Define 4 Google earnings periods to test
    google_earnings = [
        {
            "ticker": "GOOGL",
            "company": "Google/Alphabet",
            "earnings_date": "2024-10-29",
            "quarter": "Q3 2024",
            "description": "Q3 2024 - Strong cloud growth expectations"
        },
        {
            "ticker": "GOOGL",
            "company": "Google/Alphabet",
            "earnings_date": "2024-07-23",
            "quarter": "Q2 2024",
            "description": "Q2 2024 - AI investments and search revenue"
        },
        {
            "ticker": "GOOGL",
            "company": "Google/Alphabet",
            "earnings_date": "2024-04-25",
            "quarter": "Q1 2024",
            "description": "Q1 2024 - YouTube and cloud performance"
        },
        {
            "ticker": "GOOGL",
            "company": "Google/Alphabet",
            "earnings_date": "2024-01-30",
            "quarter": "Q4 2023",
            "description": "Q4 2023 - Holiday season and ad revenue"
        }
    ]
    
    all_results = []
    
    # Process each earnings period
    for i, earnings in enumerate(google_earnings, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"PROCESSING EARNINGS {i}/4: {earnings['quarter']}")
        logger.info(f"Company: {earnings['company']}")
        logger.info(f"Ticker: {earnings['ticker']}")
        logger.info(f"Earnings Date: {earnings['earnings_date']}")
        logger.info(f"Description: {earnings['description']}")
        logger.info(f"{'='*60}")
        
        try:
            # Analyze this earnings period
            result = analyzer.analyze_earnings(
                ticker=earnings['ticker'],
                company_name=earnings['company'],
                earnings_date=earnings['earnings_date']
            )
            
            if result:
                all_results.append({
                    'quarter': earnings['quarter'],
                    'earnings_date': earnings['earnings_date'],
                    'result': result
                })
                
                # Log key findings
                logger.info(f"\nKEY FINDINGS for {earnings['quarter']}:")
                logger.info(f"- Total articles analyzed: {len(result.get('articles', []))}")
                logger.info(f"- Contrarians identified: {len(result.get('contrarians', []))}")
                logger.info(f"- Market consensus: {result.get('market_consensus', 'Unknown')}")
                logger.info(f"- Investment signal: {result.get('investment_signal', 'Unknown')}")
                
                # Show top contrarians for this period
                contrarians = result.get('contrarians', [])
                if contrarians:
                    logger.info(f"\nTOP CONTRARIANS for {earnings['quarter']}:")
                    for j, contrarian in enumerate(contrarians[:3], 1):
                        logger.info(f"{j}. {contrarian.get('author', 'Unknown')} - {contrarian.get('prediction', 'Unknown')} ({contrarian.get('sentiment', 'Unknown')})")
                
            else:
                logger.warning(f"No results obtained for {earnings['quarter']}")
                
        except Exception as e:
            logger.error(f"Error processing {earnings['quarter']}: {str(e)}")
            continue
    
    # Generate comprehensive summary
    generate_pipeline_summary(analyzer, all_results, logger)
    
    return all_results

def generate_pipeline_summary(analyzer, all_results, logger):
    """Generate a comprehensive summary of the pipeline test"""
    logger.info(f"\n{'='*80}")
    logger.info("GOOGLE EARNINGS PIPELINE SUMMARY")
    logger.info(f"{'='*80}")
    
    # Overall statistics
    total_quarters = len(all_results)
    total_contrarians = sum(len(r['result'].get('contrarians', [])) for r in all_results)
    total_articles = sum(len(r['result'].get('articles', [])) for r in all_results)
    
    logger.info(f"\nOVERALL STATISTICS:")
    logger.info(f"- Quarters analyzed: {total_quarters}")
    logger.info(f"- Total articles processed: {total_articles}")
    logger.info(f"- Total contrarians identified: {total_contrarians}")
    
    if total_quarters > 0:
        logger.info(f"- Average contrarians per quarter: {total_contrarians/total_quarters:.1f}")
    else:
        logger.info(f"- Average contrarians per quarter: N/A (no successful analyses)")
    
    # Check author statistics
    try:
        stats_file = os.path.join(analyzer.database_dir, 'author_statistics.csv')
        if os.path.exists(stats_file):
            stats_df = pd.read_csv(stats_file)
            google_stats = stats_df[stats_df['company'].str.contains('Google|Alphabet', case=False, na=False)]
            
            if not google_stats.empty:
                logger.info(f"\nAUTHOR PERFORMANCE TRACKING:")
                logger.info(f"- Authors tracked for Google: {len(google_stats)}")
                
                # Top performing contrarian authors
                contrarian_authors = google_stats[google_stats['contrarian_calls'] > 0]
                if not contrarian_authors.empty:
                    top_contrarians = contrarian_authors.nlargest(5, 'contrarian_success_rate')
                    logger.info(f"\nTOP CONTRARIAN PERFORMERS:")
                    for idx, author in top_contrarians.iterrows():
                        logger.info(f"- {author['author']}: {author['contrarian_success_rate']:.1%} success rate ({author['contrarian_calls']} calls)")
                
                # Overall accuracy statistics
                avg_success_rate = google_stats['overall_success_rate'].mean()
                avg_contrarian_rate = google_stats['contrarian_success_rate'].mean()
                logger.info(f"\nACCURACY METRICS:")
                logger.info(f"- Average overall success rate: {avg_success_rate:.1%}")
                logger.info(f"- Average contrarian success rate: {avg_contrarian_rate:.1%}")
    
    except Exception as e:
        logger.warning(f"Could not load author statistics: {str(e)}")
    
    # Investment signals summary
    logger.info(f"\nINVESTMENT SIGNALS BY QUARTER:")
    for result in all_results:
        signal = result['result'].get('investment_signal', 'Unknown')
        consensus = result['result'].get('market_consensus', 'Unknown')
        logger.info(f"- {result['quarter']}: {signal} (Consensus: {consensus})")
    
    # Database files created
    logger.info(f"\nDATABASE FILES CREATED:")
    db_files = [
        'contrarian_records.csv',
        'author_statistics.csv'
    ]
    
    for db_file in db_files:
        file_path = os.path.join(analyzer.database_dir, db_file)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            logger.info(f"- {db_file}: {file_size} bytes")
        else:
            logger.info(f"- {db_file}: Not found")
    
    logger.info(f"\n{'='*80}")
    logger.info("PIPELINE TEST COMPLETED SUCCESSFULLY")
    logger.info(f"{'='*80}")

def main():
    """Main function to run the Google earnings pipeline test"""
    print("Google Earnings Pipeline Test")
    print("=============================")
    print("Testing simplified contrarian analysis across 4 Google earnings calls...\n")
    
    try:
        results = test_google_earnings_pipeline()
        
        print(f"\n✅ Pipeline test completed!")
        print(f"📊 Processed {len(results)} earnings periods")
        print(f"📁 Results saved to: simplified_contrarian_db/")
        print(f"📋 Detailed logs: google_earnings_pipeline.log")
        
        # Show quick summary
        if results:
            total_contrarians = sum(len(r['result'].get('contrarians', [])) for r in results)
            total_articles = sum(len(r['result'].get('articles', [])) for r in results)
            
            print(f"\n📈 Quick Summary:")
            print(f"   • Total articles analyzed: {total_articles}")
            print(f"   • Total contrarians identified: {total_contrarians}")
            print(f"   • Database updated with historical tracking")
        else:
            print(f"\n⚠️  No successful analyses completed")
            print(f"   • Check logs for detailed error information")
            print(f"   • Verify API keys and network connectivity")
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())