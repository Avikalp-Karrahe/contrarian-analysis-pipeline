#!/usr/bin/env python3
"""
Demo Script for Simplified Contrarian Analyzer

This script demonstrates the simplified contrarian detection system that:
1. Identifies contrarians (minority voices)
2. Tracks their accuracy over time
3. Provides simple investment signals

No complex scoring - just clear, actionable insights.
"""

import json
import pandas as pd
from simplified_contrarian_analyzer import SimplifiedContrarianAnalyzer
import os

def demo_simplified_analysis():
    """Demonstrate the simplified contrarian analysis"""
    print("=" * 60)
    print("SIMPLIFIED CONTRARIAN ANALYZER DEMO")
    print("=" * 60)
    print()
    
    # Initialize analyzer
    try:
        analyzer = SimplifiedContrarianAnalyzer()
        print("✓ Simplified Contrarian Analyzer initialized")
    except Exception as e:
        print(f"✗ Error initializing analyzer: {e}")
        return
    
    # Test companies and earnings dates
    test_cases = [
        {
            "company": "Apple",
            "symbol": "AAPL",
            "earnings_date": "2024-11-01",
            "description": "Apple Q4 2024 Earnings"
        },
        {
            "company": "Microsoft",
            "symbol": "MSFT",
            "earnings_date": "2024-10-24",
            "description": "Microsoft Q1 2025 Earnings"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-' * 50}")
        print(f"TEST CASE {i}: {test_case['description']}")
        print(f"{'-' * 50}")
        
        try:
            # Run analysis
            result = analyzer.analyze_company_earnings(
                company_name=test_case["company"],
                company_symbol=test_case["symbol"],
                earnings_date=test_case["earnings_date"],
                days_before=30
            )
            
            if 'error' in result:
                print(f"✗ Analysis failed: {result['error']}")
                continue
            
            # Display results
            print(f"\n📊 ANALYSIS SUMMARY:")
            print(f"   Company: {result['company']} ({result['symbol']})")
            print(f"   Earnings Date: {result['earnings_date']}")
            print(f"   Analysis Date: {result['analysis_date']}")
            
            summary = result['summary']
            print(f"\n📈 CONTRARIAN DETECTION:")
            print(f"   Total Articles Analyzed: {summary['total_articles_analyzed']}")
            print(f"   Contrarians Identified: {summary['contrarians_identified']}")
            print(f"   Correct Contrarians: {summary['correct_contrarians']}")
            print(f"   Contrarian Accuracy: {summary['contrarian_accuracy']}%")
            
            if result.get('actual_result'):
                actual = result['actual_result']
                print(f"\n📋 ACTUAL EARNINGS RESULT:")
                print(f"   Result: {actual['result'].upper()}")
                print(f"   Price Change: {actual['price_change_percent']}%")
            
            # Show contrarian authors
            if result.get('contrarian_authors'):
                print(f"\n👥 CONTRARIAN AUTHORS:")
                for author in result['contrarian_authors'][:5]:  # Show top 5
                    status = "✓ CORRECT" if author['was_correct'] else "✗ INCORRECT"
                    print(f"   • {author['author']} - {author['prediction'].upper()} ({author['sentiment']}) {status}")
                    print(f"     Headline: {author['headline'][:80]}...")
            
            # Show investment signals
            signals = result.get('investment_signals', {})
            print(f"\n🎯 INVESTMENT SIGNALS:")
            print(f"   Recommendation: {signals.get('recommendation', 'N/A')}")
            print(f"   Confidence: {signals.get('confidence', 'N/A')}")
            print(f"   Reliable Contrarians Found: {signals.get('reliable_contrarians_count', 0)}")
            
            if signals.get('top_contrarians'):
                print(f"\n🏆 TOP CONTRARIAN PERFORMERS:")
                for contrarian in signals['top_contrarians'][:3]:
                    print(f"   • {contrarian['author']}: {contrarian['contrarian_accuracy']}% accuracy ({contrarian['contrarian_predictions']} predictions)")
            
        except Exception as e:
            print(f"✗ Error in analysis: {e}")
    
    # Show database summary
    print(f"\n{'-' * 50}")
    print("DATABASE SUMMARY")
    print(f"{'-' * 50}")
    
    try:
        # Check if database files exist
        records_file = os.path.join(analyzer.database_dir, "contrarian_records.csv")
        stats_file = os.path.join(analyzer.database_dir, "author_statistics.csv")
        
        if os.path.exists(records_file):
            records_df = pd.read_csv(records_file)
            print(f"\n📁 CONTRARIAN RECORDS:")
            print(f"   Total Records: {len(records_df)}")
            print(f"   Unique Authors: {records_df['author'].nunique()}")
            print(f"   Companies Covered: {records_df['company'].nunique()}")
            
            # Show recent records
            if len(records_df) > 0:
                print(f"\n📝 RECENT RECORDS:")
                recent = records_df.tail(5)
                for _, record in recent.iterrows():
                    status = "CONTRARIAN" if record['was_contrarian'] else "CONSENSUS"
                    accuracy = "CORRECT" if record['was_correct'] else "INCORRECT"
                    print(f"   • {record['author']} - {record['company']} - {status} - {accuracy}")
        
        if os.path.exists(stats_file):
            stats_df = pd.read_csv(stats_file)
            print(f"\n📊 AUTHOR STATISTICS:")
            print(f"   Authors Tracked: {len(stats_df)}")
            
            if len(stats_df) > 0:
                # Show top performers
                top_performers = stats_df[
                    (stats_df['contrarian_predictions'] >= 2) & 
                    (stats_df['contrarian_accuracy'] > 0)
                ].sort_values('contrarian_accuracy', ascending=False).head(5)
                
                if len(top_performers) > 0:
                    print(f"\n🎖️ TOP CONTRARIAN PERFORMERS:")
                    for _, author in top_performers.iterrows():
                        print(f"   • {author['author']}: {author['contrarian_accuracy']}% accuracy")
                        print(f"     Total: {author['total_predictions']} predictions, Contrarian: {author['contrarian_predictions']}")
                        print(f"     Specialization: {author['specialization']}, Recent streak: {author['recent_streak']}/5")
    
    except Exception as e:
        print(f"✗ Error reading database: {e}")
    
    print(f"\n{'-' * 50}")
    print("KEY BENEFITS OF SIMPLIFIED SYSTEM:")
    print(f"{'-' * 50}")
    print("✓ Easy to understand: Contrarian vs Consensus")
    print("✓ Clear accuracy tracking: Correct vs Incorrect")
    print("✓ Actionable insights: Simple investment signals")
    print("✓ Historical performance: Track authors over time")
    print("✓ No complex scoring: Focus on what matters")
    print("✓ Scalable: Works across multiple companies")
    
    print(f"\n{'-' * 50}")
    print("INVESTMENT DECISION FRAMEWORK:")
    print(f"{'-' * 50}")
    print("🟢 STRONG SIGNAL: 5+ reliable contrarians (>60% accuracy)")
    print("🟡 CONSIDER: 3-4 reliable contrarians")
    print("🔴 MONITOR: <3 reliable contrarians")
    print("")
    print("Focus on authors with:")
    print("• High contrarian accuracy (>60%)")
    print("• Consistent activity (3+ contrarian calls)")
    print("• Recent good performance")
    
    print(f"\n{'=' * 60}")
    print("DEMO COMPLETED")
    print(f"{'=' * 60}")

def show_database_contents():
    """Show current database contents"""
    print("\n" + "=" * 60)
    print("DATABASE CONTENTS")
    print("=" * 60)
    
    database_dir = "simplified_contrarian_db"
    records_file = os.path.join(database_dir, "contrarian_records.csv")
    stats_file = os.path.join(database_dir, "author_statistics.csv")
    
    # Show records
    if os.path.exists(records_file):
        print("\n📁 CONTRARIAN RECORDS:")
        df = pd.read_csv(records_file)
        print(df.to_string(index=False, max_rows=10))
        
        if len(df) > 10:
            print(f"\n... and {len(df) - 10} more records")
    
    # Show statistics
    if os.path.exists(stats_file):
        print("\n📊 AUTHOR STATISTICS:")
        df = pd.read_csv(stats_file)
        print(df.to_string(index=False))

if __name__ == "__main__":
    # Run the demo
    demo_simplified_analysis()
    
    # Optionally show database contents
    show_database_contents()