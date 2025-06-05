#!/usr/bin/env python3
"""
Demo: Master Contrarian Tracking System

This script demonstrates how to use the master contrarian database to track
analysts across multiple earnings calls and companies, identifying repeat
contrarians and their historical performance.
"""

import os
import json
import pandas as pd
from datetime import datetime
from master_contrarian_database import MasterContrarianDatabase
from contrarian_csv_exporter import ContrarianCSVExporter

def demo_master_contrarian_system():
    """
    Demonstrate the master contrarian tracking system
    """
    print("=" * 60)
    print("MASTER CONTRARIAN TRACKING SYSTEM DEMO")
    print("=" * 60)
    
    # Initialize the master database
    print("\n1. Initializing Master Contrarian Database...")
    master_db = MasterContrarianDatabase()
    print(f"   Database location: {master_db.master_csv_path}")
    print(f"   Author histories: {master_db.author_history_dir}")
    
    # Check for existing analysis reports
    print("\n2. Scanning for existing contrarian analysis reports...")
    outputs_dir = "outputs"
    json_reports = []
    
    if os.path.exists(outputs_dir):
        for root, dirs, files in os.walk(outputs_dir):
            for file in files:
                if file.endswith('.json') and 'contrarian' in file.lower():
                    json_reports.append(os.path.join(root, file))
    
    print(f"   Found {len(json_reports)} contrarian analysis reports")
    
    if not json_reports:
        print("   No existing reports found. Creating sample data...")
        create_sample_contrarian_data(master_db)
    else:
        # Process existing reports
        print("\n3. Processing existing contrarian reports...")
        for i, report_path in enumerate(json_reports, 1):
            print(f"   Processing report {i}/{len(json_reports)}: {os.path.basename(report_path)}")
            process_contrarian_report(master_db, report_path)
    
    # Display database statistics
    print("\n4. Master Database Statistics:")
    display_database_stats(master_db)
    
    # Show top contrarians
    print("\n5. Top Performing Contrarians:")
    show_top_contrarians(master_db)
    
    # Show repeat contrarians
    print("\n6. Repeat Contrarians (Multiple Instances):")
    show_repeat_contrarians(master_db)
    
    # Show author history example
    print("\n7. Individual Author History Example:")
    show_author_history_example(master_db)
    
    # Export master database summary
    print("\n8. Exporting Master Database Summary...")
    export_master_summary(master_db)
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)

def process_contrarian_report(master_db: MasterContrarianDatabase, report_path: str):
    """
    Process a contrarian analysis report and update the master database
    """
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        contrarians = report_data.get('contrarian_analysts', [])
        if contrarians:
            master_db.add_contrarian_analysis(report_data, contrarians)
            print(f"     Added {len(contrarians)} contrarian(s) to master database")
        else:
            print(f"     No contrarians found in {os.path.basename(report_path)}")
    
    except Exception as e:
        print(f"     Error processing {os.path.basename(report_path)}: {e}")

def create_sample_contrarian_data(master_db: MasterContrarianDatabase):
    """
    Create sample contrarian data for demonstration
    """
    print("   Creating sample contrarian data...")
    
    # Sample contrarian data for different companies and dates
    sample_reports = [
        {
            'company': 'Apple Inc.',
            'symbol': 'AAPL',
            'earnings_date': '2024-01-25',
            'actual_result': {'result': 'beat', 'eps_actual': 2.18, 'eps_estimate': 2.10},
            'contrarian_analysts': [
                {
                    'author': 'John Smith',
                    'sentiment': 'bullish',
                    'earnings_prediction': 'beat',
                    'was_minority_sentiment': True,
                    'was_minority_prediction': True,
                    'contrarian_score': 8.5,
                    'reasoning': 'Strong iPhone sales expected despite market pessimism',
                    'key_concerns': ['Supply chain improvements', 'Holiday sales momentum']
                },
                {
                    'author': 'Sarah Johnson',
                    'sentiment': 'bearish',
                    'earnings_prediction': 'beat',
                    'was_minority_sentiment': False,
                    'was_minority_prediction': True,
                    'contrarian_score': 7.2,
                    'reasoning': 'Earnings will beat but stock overvalued',
                    'key_concerns': ['Valuation concerns', 'Market saturation']
                }
            ]
        },
        {
            'company': 'Microsoft Corporation',
            'symbol': 'MSFT',
            'earnings_date': '2024-01-24',
            'actual_result': {'result': 'miss', 'eps_actual': 2.93, 'eps_estimate': 2.99},
            'contrarian_analysts': [
                {
                    'author': 'John Smith',
                    'sentiment': 'bearish',
                    'earnings_prediction': 'miss',
                    'was_minority_sentiment': True,
                    'was_minority_prediction': True,
                    'contrarian_score': 9.1,
                    'reasoning': 'Cloud growth slowing, Azure competition intensifying',
                    'key_concerns': ['Azure growth deceleration', 'Increased competition']
                }
            ]
        },
        {
            'company': 'Apple Inc.',
            'symbol': 'AAPL',
            'earnings_date': '2023-10-26',
            'actual_result': {'result': 'beat', 'eps_actual': 1.46, 'eps_estimate': 1.39},
            'contrarian_analysts': [
                {
                    'author': 'John Smith',
                    'sentiment': 'bullish',
                    'earnings_prediction': 'beat',
                    'was_minority_sentiment': True,
                    'was_minority_prediction': True,
                    'contrarian_score': 8.8,
                    'reasoning': 'iPhone 15 launch momentum stronger than expected',
                    'key_concerns': ['New product cycle', 'Market share gains']
                },
                {
                    'author': 'Mike Davis',
                    'sentiment': 'neutral',
                    'earnings_prediction': 'miss',
                    'was_minority_sentiment': False,
                    'was_minority_prediction': True,
                    'contrarian_score': 6.5,
                    'reasoning': 'Economic headwinds will impact consumer spending',
                    'key_concerns': ['Economic uncertainty', 'Consumer spending']
                }
            ]
        }
    ]
    
    # Add sample data to master database
    for report in sample_reports:
        master_db.add_contrarian_analysis(report, report['contrarian_analysts'])
    
    print(f"   Created sample data for {len(sample_reports)} earnings reports")

def display_database_stats(master_db: MasterContrarianDatabase):
    """
    Display statistics from the master database
    """
    try:
        if os.path.exists(master_db.master_csv_path):
            df = pd.read_csv(master_db.master_csv_path)
            
            print(f"   Total Authors Tracked: {len(df)}")
            print(f"   Total Contrarian Instances: {df['Total_Contrarian_Instances'].sum()}")
            print(f"   Authors with Multiple Instances: {len(df[df['Total_Contrarian_Instances'] > 1])}")
            print(f"   Average Success Rate: {df['Contrarian_Success_Rate'].mean():.1f}%")
            print(f"   Companies Covered: {len(set([comp for comps in df['Companies_List'].dropna() for comp in comps.split(';')]))}")
        else:
            print("   Master database is empty")
    except Exception as e:
        print(f"   Error reading database stats: {e}")

def show_top_contrarians(master_db: MasterContrarianDatabase, limit: int = 5):
    """
    Show top performing contrarians
    """
    try:
        top_contrarians = master_db.get_top_contrarians(limit, 'Contrarian_Success_Rate')
        
        if not top_contrarians.empty:
            print(f"   Top {limit} Contrarians by Success Rate:")
            for i, (_, row) in enumerate(top_contrarians.iterrows(), 1):
                success_rate = row['Contrarian_Success_Rate']
                instances = row['Total_Contrarian_Instances']
                companies = row['Total_Companies_Covered']
                print(f"   {i}. {row['Author_Name']}")
                print(f"      Success Rate: {success_rate:.1f}% ({instances} instances across {companies} companies)")
                print(f"      Latest: {row['Latest_Company']} ({row['Latest_Earnings_Date']})")
                print(f"      Risk Level: {row['Risk_Level']}")
                print()
        else:
            print("   No contrarian data available")
    except Exception as e:
        print(f"   Error showing top contrarians: {e}")

def show_repeat_contrarians(master_db: MasterContrarianDatabase, min_instances: int = 2):
    """
    Show authors who have been contrarians multiple times
    """
    try:
        repeat_contrarians = master_db.get_repeat_contrarians(min_instances)
        
        if not repeat_contrarians.empty:
            print(f"   Authors with {min_instances}+ Contrarian Instances:")
            for i, (_, row) in enumerate(repeat_contrarians.iterrows(), 1):
                instances = row['Total_Contrarian_Instances']
                companies = row['Total_Companies_Covered']
                consistency = row['Consistency_Score']
                print(f"   {i}. {row['Author_Name']}")
                print(f"      Instances: {instances} across {companies} companies")
                print(f"      Consistency Score: {consistency:.1f}%")
                print(f"      Companies: {row['Companies_List']}")
                print(f"      Date Range: {row['First_Seen_Date']} to {row['Last_Seen_Date']}")
                print()
        else:
            print(f"   No authors with {min_instances}+ contrarian instances found")
    except Exception as e:
        print(f"   Error showing repeat contrarians: {e}")

def show_author_history_example(master_db: MasterContrarianDatabase):
    """
    Show detailed history for one author as an example
    """
    try:
        if os.path.exists(master_db.master_csv_path):
            df = pd.read_csv(master_db.master_csv_path)
            
            if not df.empty:
                # Get author with most instances
                top_author = df.loc[df['Total_Contrarian_Instances'].idxmax()]
                author_name = top_author['Author_Name']
                
                print(f"   Detailed History for: {author_name}")
                print(f"   Total Instances: {top_author['Total_Contrarian_Instances']}")
                print(f"   Success Rate: {top_author['Contrarian_Success_Rate']:.1f}%")
                print(f"   Companies Covered: {top_author['Companies_List']}")
                
                # Get detailed history
                history = master_db.get_author_history(author_name)
                if history is not None and not history.empty:
                    print(f"\n   Individual Contrarian Calls:")
                    for i, (_, call) in enumerate(history.iterrows(), 1):
                        print(f"   {i}. {call['Company']} ({call['Symbol']}) - {call['Earnings_Date']}")
                        print(f"      Prediction: {call['Earnings_Prediction']} | Sentiment: {call['Sentiment']}")
                        print(f"      Was Correct: {call['Was_Correct']} | Score: {call['Contrarian_Score']}")
                        print(f"      Reasoning: {call['Reasoning'][:100]}...")
                        print()
            else:
                print("   No author data available")
        else:
            print("   Master database not found")
    except Exception as e:
        print(f"   Error showing author history: {e}")

def export_master_summary(master_db: MasterContrarianDatabase):
    """
    Export master database summary
    """
    try:
        exporter = ContrarianCSVExporter()
        summary_path = exporter.export_master_database_summary()
        
        if summary_path:
            print(f"   Master database summary exported to: {summary_path}")
            
            # Also show some quick stats
            stats = exporter.get_master_database_stats()
            if 'error' not in stats:
                print(f"   Quick Stats:")
                print(f"     Total Authors: {stats['total_authors']}")
                print(f"     Total Instances: {stats['total_contrarian_instances']}")
                print(f"     Repeat Contrarians: {stats['repeat_contrarians']}")
                print(f"     Average Success Rate: {stats['avg_success_rate']:.1f}%")
                if stats['top_performer']:
                    print(f"     Top Performer: {stats['top_performer']}")
                if stats['most_active']:
                    print(f"     Most Active: {stats['most_active']}")
        else:
            print("   Failed to export master database summary")
    except Exception as e:
        print(f"   Error exporting summary: {e}")

def main():
    """
    Main function to run the demo
    """
    try:
        demo_master_contrarian_system()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()