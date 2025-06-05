#!/usr/bin/env python3
"""
Command-line interface for Production Contrarian Earnings Analyzer

Usage examples:
    python run_production_contrarian_analysis.py --company "Apple" --symbol "AAPL" --date "2024-11-01"
    python run_production_contrarian_analysis.py --company "Microsoft" --symbol "MSFT" --date "2024-10-24" --days 45 --max-articles 40
    python run_production_contrarian_analysis.py --company "Tesla" --symbol "TSLA" --date "2024-10-23" --conservative
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
import logging

# Add the src directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

from analyzers.contrarian_earnings_analyzer_production import ProductionContrarianEarningsAnalyzer, RateLimitConfig
from analyzers.contrarian_csv_exporter import ContrarianCSVExporter

def validate_date(date_string):
    """Validate date format and check if it's reasonable"""
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        
        # Check if date is too far in the future
        if date_obj > datetime.now() + timedelta(days=365):
            print(f"Warning: Earnings date {date_string} is more than a year in the future.")
            
        # Check if date is too far in the past (before 2020)
        if date_obj < datetime(2020, 1, 1):
            print(f"Warning: Earnings date {date_string} is before 2020. Limited data may be available.")
            
        return date_obj
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}. Use YYYY-MM-DD format.")

def validate_positive_int(value):
    """Validate positive integer"""
    try:
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(f"Value must be positive: {value}")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer: {value}")

def main():
    parser = argparse.ArgumentParser(
        description="Production Contrarian Earnings Analyzer - Identify minority voices who were proven right",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --company "Apple" --symbol "AAPL" --date "2024-11-01"
  %(prog)s --company "Microsoft" --symbol "MSFT" --date "2024-10-24" --days 45 --max-articles 40
  %(prog)s --company "Tesla" --symbol "TSLA" --date "2024-10-23" --conservative
  %(prog)s --company "NVIDIA" --symbol "NVDA" --date "2024-08-28" --days 21 --output "nvidia_q2_2024.json"

Note: Use past earnings dates for best results as actual earnings data is needed for contrarian identification.
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--company", "-c",
        required=True,
        help="Company name to analyze (e.g., 'Apple', 'Microsoft')"
    )
    
    parser.add_argument(
        "--symbol", "-s",
        required=True,
        help="Stock symbol (e.g., 'AAPL', 'MSFT')"
    )
    
    parser.add_argument(
        "--date", "-d",
        required=True,
        type=validate_date,
        help="Earnings date in YYYY-MM-DD format"
    )
    
    # Optional arguments
    parser.add_argument(
        "--days",
        type=validate_positive_int,
        default=30,
        help="Number of days before earnings to search for articles (default: 30)"
    )
    
    parser.add_argument(
        "--max-articles",
        type=validate_positive_int,
        default=30,
        help="Maximum number of articles to analyze (default: 30)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output filename (default: auto-generated with timestamp)"
    )
    
    # Rate limiting options
    rate_group = parser.add_argument_group("Rate Limiting Options")
    
    rate_group.add_argument(
        "--conservative",
        action="store_true",
        help="Use conservative rate limits (slower but safer for free APIs)"
    )
    
    rate_group.add_argument(
        "--guardian-rate",
        type=validate_positive_int,
        help="Guardian API requests per minute (default: 12 for free tier)"
    )
    
    rate_group.add_argument(
        "--groq-rate",
        type=validate_positive_int,
        help="Groq API requests per minute (default: 30 for free tier)"
    )
    
    # Logging options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress most output (errors only)"
    )
    
    # Validation options
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompts"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    # Validate inputs
    earnings_date_str = args.date.strftime("%Y-%m-%d")
    
    # Check if earnings date is in the future
    if args.date > datetime.now():
        if not args.force:
            response = input(f"Earnings date {earnings_date_str} is in the future. Actual earnings data won't be available. Continue? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("Analysis cancelled.")
                sys.exit(0)
    
    # Setup rate limiting configuration
    if args.conservative:
        rate_config = RateLimitConfig(
            guardian_requests_per_minute=8,   # Very conservative
            groq_requests_per_minute=20,      # Very conservative
            min_delay_between_requests=2.0,
            max_delay_between_requests=4.0
        )
        print("Using conservative rate limits for maximum API safety.")
    else:
        rate_config = RateLimitConfig(
            guardian_requests_per_minute=args.guardian_rate or 12,
            groq_requests_per_minute=args.groq_rate or 30,
            min_delay_between_requests=1.0,
            max_delay_between_requests=2.5
        )
    
    # Display analysis parameters
    print("\n" + "="*60)
    print("PRODUCTION CONTRARIAN EARNINGS ANALYSIS")
    print("="*60)
    print(f"Company: {args.company}")
    print(f"Symbol: {args.symbol}")
    print(f"Earnings Date: {earnings_date_str}")
    print(f"Search Period: {args.days} days before earnings")
    print(f"Max Articles: {args.max_articles}")
    print(f"Rate Limits: Guardian {rate_config.guardian_requests_per_minute}/min, Groq {rate_config.groq_requests_per_minute}/min")
    
    if not args.force:
        response = input("\nProceed with analysis? (Y/n): ")
        if response.lower() in ['n', 'no']:
            print("Analysis cancelled.")
            sys.exit(0)
    
    print("\nStarting analysis...")
    print("This may take several minutes depending on the number of articles and rate limits.")
    print("Progress will be logged below:\n")
    
    try:
        # Initialize analyzer
        analyzer = ProductionContrarianEarningsAnalyzer(rate_config)
        
        # Run analysis
        report = analyzer.analyze_company_earnings(
            company_name=args.company,
            company_symbol=args.symbol,
            earnings_date=earnings_date_str,
            days_before=args.days,
            max_articles=args.max_articles
        )
        
        if not report:
            print("\nAnalysis failed. Check the logs above for details.")
            sys.exit(1)
        
        # Save report
        filepath = analyzer.save_report(report, args.output)
        
        # Export to CSV
        print("\nExporting data to CSV files...")
        csv_exporter = ContrarianCSVExporter(create_run_folder=True)
        exported_csv_files = csv_exporter.export_full_analysis(report)
        
        if exported_csv_files:
            print("\nCSV files exported:")
            for csv_file in exported_csv_files:
                print(f"  - {csv_file}")
        else:
            print("  No CSV files exported (possibly no data)")
        
        # Display results
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        
        # Basic stats
        print(f"Analysis completed in {report['analysis_parameters']['analysis_duration_seconds']} seconds")
        print(f"Articles found: {report['data_collection']['total_articles_found']}")
        print(f"Articles analyzed: {report['data_collection']['articles_analyzed']}")
        print(f"Successful analyses: {report['data_collection']['successful_analyses']}")
        print(f"API usage: Guardian {report['api_usage']['guardian_requests']}, Groq {report['api_usage']['groq_requests']}")
        
        # Actual results
        if report['actual_result']:
            actual = report['actual_result']
            print(f"\nACTUAL EARNINGS RESULT:")
            print(f"  Price change: {actual['price_change_percent']}%")
            print(f"  Result: {actual['result'].upper()}")
            print(f"  Volume change: {actual['volume_change_percent']}%")
            print(f"  Data from: {actual['actual_date_used']}")
        else:
            print(f"\nACTUAL EARNINGS RESULT: Not available")
        
        # Contrarian results
        print(f"\nCONTRARIAN ANALYSIS:")
        print(f"  Contrarians found: {report['contrarians_found']}")
        
        if report['contrarians_found'] > 0:
            print(f"  Average contrarian score: {report['summary']['avg_contrarian_score']}")
            
            print(f"\nTOP CONTRARIANS:")
            for i, contrarian in enumerate(report['contrarian_analysts'][:5], 1):
                print(f"\n  {i}. {contrarian['author']}")
                print(f"     Score: {contrarian['contrarian_score']}")
                print(f"     Headline: {contrarian['headline'][:70]}...")
                print(f"     Sentiment: {contrarian['sentiment']} ({contrarian['sentiment_percentage']}% had this view)")
                print(f"     Prediction: {contrarian['prediction']} ({contrarian['prediction_percentage']}% had this view)")
                print(f"     Correct on: Sentiment={contrarian['sentiment_correct']}, Prediction={contrarian['prediction_correct']}")
                print(f"     Confidence: {contrarian['confidence']} sentiment, {contrarian['prediction_confidence']} prediction")
        else:
            print("  No contrarians identified in this analysis.")
            print("  This could mean:")
            print("    - The majority view was correct")
            print("    - No clear minority positions were taken")
            print("    - Insufficient data for contrarian identification")
        
        # Market consensus
        print(f"\nMARKET CONSENSUS:")
        print(f"  Sentiment distribution: {report['summary']['sentiment_distribution']}")
        print(f"  Prediction distribution: {report['summary']['prediction_distribution']}")
        
        print(f"\nDetailed report saved to: {filepath}")
        print(f"\nAnalysis complete! 🎯")
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAnalysis failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()