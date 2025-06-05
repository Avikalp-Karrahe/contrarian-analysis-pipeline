#!/usr/bin/env python3
"""
Realistic Google Earnings Pipeline Demo

This script demonstrates the simplified contrarian analysis pipeline using a more realistic
approach that simulates Google earnings analysis with sample data to show how the system
works when articles are available.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import pandas as pd
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simplified_contrarian_analyzer import SimplifiedContrarianAnalyzer, ContrarianRecord

def setup_logging():
    """Setup logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('google_realistic_demo.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def simulate_google_earnings_analysis():
    """Simulate Google earnings analysis with realistic sample data"""
    logger = setup_logging()
    logger.info("Starting Realistic Google Earnings Analysis Demo")
    
    # Initialize the simplified contrarian analyzer
    analyzer = SimplifiedContrarianAnalyzer()
    
    # Sample Google earnings scenarios
    google_scenarios = [
        {
            "quarter": "Q3 2024",
            "earnings_date": "2024-10-29",
            "actual_result": "beat",  # Google actually beat expectations
            "description": "Strong cloud growth and AI investments",
            "sample_articles": [
                {
                    "author": "Alex Thompson",
                    "headline": "Google's Cloud Business May Disappoint Despite AI Hype",
                    "sentiment": "bearish",
                    "prediction": "miss",
                    "reasoning": "Competition from Microsoft and Amazon intensifying"
                },
                {
                    "author": "Sarah Chen",
                    "headline": "Alphabet Poised for Strong Quarter on Search Revenue",
                    "sentiment": "bullish",
                    "prediction": "beat",
                    "reasoning": "Search advertising remains robust"
                },
                {
                    "author": "Michael Rodriguez",
                    "headline": "Google's AI Spending Could Hurt Near-term Profits",
                    "sentiment": "bearish",
                    "prediction": "miss",
                    "reasoning": "Heavy investment in AI infrastructure"
                },
                {
                    "author": "Jennifer Kim",
                    "headline": "YouTube Revenue Growth Expected to Accelerate",
                    "sentiment": "bullish",
                    "prediction": "beat",
                    "reasoning": "Strong advertiser demand and creator economy"
                },
                {
                    "author": "David Park",
                    "headline": "Regulatory Concerns May Weigh on Alphabet Stock",
                    "sentiment": "bearish",
                    "prediction": "miss",
                    "reasoning": "Antitrust investigations creating uncertainty"
                }
            ]
        },
        {
            "quarter": "Q2 2024",
            "earnings_date": "2024-07-23",
            "actual_result": "meet",  # Met expectations
            "description": "Mixed results with strong search, weak other bets",
            "sample_articles": [
                {
                    "author": "Lisa Wang",
                    "headline": "Google's Other Bets Division Continues to Bleed Money",
                    "sentiment": "bearish",
                    "prediction": "miss",
                    "reasoning": "Waymo and other ventures burning cash"
                },
                {
                    "author": "Robert Johnson",
                    "headline": "Alphabet's Core Search Business Remains Unshakeable",
                    "sentiment": "bullish",
                    "prediction": "beat",
                    "reasoning": "Market dominance in search advertising"
                },
                {
                    "author": "Emily Davis",
                    "headline": "Google Cloud Growth May Be Slowing Down",
                    "sentiment": "bearish",
                    "prediction": "miss",
                    "reasoning": "Market saturation and increased competition"
                }
            ]
        }
    ]
    
    all_results = []
    
    # Process each scenario
    for i, scenario in enumerate(google_scenarios, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"ANALYZING SCENARIO {i}/2: {scenario['quarter']}")
        logger.info(f"Earnings Date: {scenario['earnings_date']}")
        logger.info(f"Actual Result: {scenario['actual_result']}")
        logger.info(f"Description: {scenario['description']}")
        logger.info(f"{'='*60}")
        
        # Simulate the analysis process
        articles = scenario['sample_articles']
        
        # Determine consensus
        predictions = [article['prediction'] for article in articles]
        sentiment_counts = {'bullish': 0, 'bearish': 0, 'neutral': 0}
        prediction_counts = {'beat': 0, 'miss': 0, 'meet': 0}
        
        for article in articles:
            sentiment_counts[article['sentiment']] += 1
            prediction_counts[article['prediction']] += 1
        
        # Determine market consensus
        consensus_prediction = max(prediction_counts, key=prediction_counts.get)
        consensus_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        
        logger.info(f"\nMARKET CONSENSUS ANALYSIS:")
        logger.info(f"- Prediction consensus: {consensus_prediction}")
        logger.info(f"- Sentiment consensus: {consensus_sentiment}")
        logger.info(f"- Prediction breakdown: {prediction_counts}")
        logger.info(f"- Sentiment breakdown: {sentiment_counts}")
        
        # Identify contrarians
        contrarians = []
        for article in articles:
            is_contrarian = (
                article['prediction'] != consensus_prediction or
                article['sentiment'] != consensus_sentiment
            )
            
            if is_contrarian:
                # Check if contrarian was correct
                was_correct = article['prediction'] == scenario['actual_result']
                
                contrarian_info = {
                    'author': article['author'],
                    'headline': article['headline'],
                    'prediction': article['prediction'],
                    'sentiment': article['sentiment'],
                    'was_correct': was_correct,
                    'reasoning': article['reasoning']
                }
                contrarians.append(contrarian_info)
                
                # Create contrarian record
                record = ContrarianRecord(
                    author=article['author'],
                    company="Google/Alphabet",
                    symbol="GOOGL",
                    earnings_date=scenario['earnings_date'],
                    prediction=article['prediction'],
                    sentiment=article['sentiment'],
                    was_contrarian=True,
                    was_correct=was_correct,
                    actual_result=scenario['actual_result'],
                    date_analyzed=datetime.now().strftime('%Y-%m-%d'),
                    headline=article['headline'],
                    url=f"https://example.com/google-article-{i}-{len(contrarians)}"
                )
                
                # Save to database
                analyzer.save_records([record])
        
        logger.info(f"\nCONTRARIAN ANALYSIS:")
        logger.info(f"- Total contrarians identified: {len(contrarians)}")
        
        if contrarians:
            correct_contrarians = [c for c in contrarians if c['was_correct']]
            logger.info(f"- Correct contrarians: {len(correct_contrarians)}")
            logger.info(f"- Contrarian accuracy: {len(correct_contrarians)/len(contrarians):.1%}")
            
            logger.info(f"\nTOP CONTRARIANS:")
            for j, contrarian in enumerate(contrarians, 1):
                status = "✅ CORRECT" if contrarian['was_correct'] else "❌ INCORRECT"
                logger.info(f"{j}. {contrarian['author']} - {contrarian['prediction']} ({contrarian['sentiment']}) {status}")
                logger.info(f"   Reasoning: {contrarian['reasoning']}")
        
        # Generate investment signal
        if contrarians:
            correct_contrarians = [c for c in contrarians if c['was_correct']]
            contrarian_accuracy = len(correct_contrarians) / len(contrarians)
            
            if contrarian_accuracy >= 0.6 and len(contrarians) >= 2:
                signal = "STRONG_CONTRARIAN"
            elif contrarian_accuracy >= 0.4:
                signal = "MODERATE_CONTRARIAN"
            else:
                signal = "FOLLOW_CONSENSUS"
        else:
            signal = "FOLLOW_CONSENSUS"
        
        logger.info(f"\nINVESTMENT SIGNAL: {signal}")
        
        result = {
            'quarter': scenario['quarter'],
            'earnings_date': scenario['earnings_date'],
            'actual_result': scenario['actual_result'],
            'consensus_prediction': consensus_prediction,
            'consensus_sentiment': consensus_sentiment,
            'contrarians': contrarians,
            'investment_signal': signal,
            'total_articles': len(articles)
        }
        
        all_results.append(result)
    
    # Update author statistics
    analyzer.update_author_statistics()
    
    # Generate comprehensive summary
    generate_realistic_summary(analyzer, all_results, logger)
    
    return all_results

def generate_realistic_summary(analyzer, all_results, logger):
    """Generate a comprehensive summary of the realistic demo"""
    logger.info(f"\n{'='*80}")
    logger.info("REALISTIC GOOGLE EARNINGS ANALYSIS SUMMARY")
    logger.info(f"{'='*80}")
    
    # Overall statistics
    total_quarters = len(all_results)
    total_contrarians = sum(len(r['contrarians']) for r in all_results)
    total_articles = sum(r['total_articles'] for r in all_results)
    
    logger.info(f"\nOVERALL STATISTICS:")
    logger.info(f"- Quarters analyzed: {total_quarters}")
    logger.info(f"- Total articles processed: {total_articles}")
    logger.info(f"- Total contrarians identified: {total_contrarians}")
    logger.info(f"- Average contrarians per quarter: {total_contrarians/total_quarters:.1f}")
    
    # Contrarian accuracy analysis
    all_contrarians = []
    for result in all_results:
        all_contrarians.extend(result['contrarians'])
    
    if all_contrarians:
        correct_contrarians = [c for c in all_contrarians if c['was_correct']]
        overall_accuracy = len(correct_contrarians) / len(all_contrarians)
        
        logger.info(f"\nCONTRARIAN PERFORMANCE:")
        logger.info(f"- Overall contrarian accuracy: {overall_accuracy:.1%}")
        logger.info(f"- Correct contrarian calls: {len(correct_contrarians)}")
        logger.info(f"- Incorrect contrarian calls: {len(all_contrarians) - len(correct_contrarians)}")
        
        # Top performing contrarians
        author_performance = {}
        for contrarian in all_contrarians:
            author = contrarian['author']
            if author not in author_performance:
                author_performance[author] = {'total': 0, 'correct': 0}
            author_performance[author]['total'] += 1
            if contrarian['was_correct']:
                author_performance[author]['correct'] += 1
        
        logger.info(f"\nTOP CONTRARIAN PERFORMERS:")
        for author, stats in sorted(author_performance.items(), 
                                  key=lambda x: x[1]['correct']/x[1]['total'], 
                                  reverse=True):
            accuracy = stats['correct'] / stats['total']
            logger.info(f"- {author}: {accuracy:.1%} accuracy ({stats['correct']}/{stats['total']})")
    
    # Investment signals summary
    logger.info(f"\nINVESTMENT SIGNALS BY QUARTER:")
    for result in all_results:
        logger.info(f"- {result['quarter']}: {result['investment_signal']} (Actual: {result['actual_result']})")
    
    # Database status
    logger.info(f"\nDATABASE STATUS:")
    records_file = os.path.join(analyzer.database_dir, 'contrarian_records.csv')
    stats_file = os.path.join(analyzer.database_dir, 'author_statistics.csv')
    
    if os.path.exists(records_file):
        records_size = os.path.getsize(records_file)
        logger.info(f"- contrarian_records.csv: {records_size} bytes")
    
    if os.path.exists(stats_file):
        stats_size = os.path.getsize(stats_file)
        logger.info(f"- author_statistics.csv: {stats_size} bytes")
    
    logger.info(f"\n{'='*80}")
    logger.info("REALISTIC DEMO COMPLETED SUCCESSFULLY")
    logger.info(f"{'='*80}")

def main():
    """Main function to run the realistic Google earnings demo"""
    print("Realistic Google Earnings Analysis Demo")
    print("======================================")
    print("Demonstrating simplified contrarian analysis with sample Google earnings data...\n")
    
    try:
        results = simulate_google_earnings_analysis()
        
        print(f"\n✅ Demo completed successfully!")
        print(f"📊 Analyzed {len(results)} earnings scenarios")
        print(f"📁 Results saved to: simplified_contrarian_db/")
        print(f"📋 Detailed logs: google_realistic_demo.log")
        
        # Show quick summary
        total_contrarians = sum(len(r['contrarians']) for r in results)
        total_articles = sum(r['total_articles'] for r in results)
        
        print(f"\n📈 Quick Summary:")
        print(f"   • Total sample articles: {total_articles}")
        print(f"   • Contrarians identified: {total_contrarians}")
        print(f"   • Database updated with tracking data")
        
        # Show contrarian accuracy
        all_contrarians = []
        for result in results:
            all_contrarians.extend(result['contrarians'])
        
        if all_contrarians:
            correct = sum(1 for c in all_contrarians if c['was_correct'])
            accuracy = correct / len(all_contrarians)
            print(f"   • Contrarian accuracy: {accuracy:.1%} ({correct}/{len(all_contrarians)})")
        
        print(f"\n🎯 This demo shows how the system would work with real Google earnings data!")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())