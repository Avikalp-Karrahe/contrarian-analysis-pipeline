#!/usr/bin/env python3
"""
Simplified Contrarian Earnings Analyzer

This system identifies contrarian analysts/authors who predicted against the consensus
and tracks their historical accuracy over time. The focus is on simplicity and
actionable insights rather than complex scoring.

Key Features:
- Simple contrarian identification (minority vs consensus)
- Binary accuracy tracking (correct/incorrect)
- Historical performance records
- Clean, actionable reporting
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from collections import defaultdict, Counter
import yfinance as yf
from groq import Groq
import logging
import time
from typing import List, Dict, Optional
import random
from dataclasses import dataclass
import csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simplified_contrarian_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ContrarianRecord:
    """Simple record for tracking contrarian predictions"""
    author: str
    company: str
    symbol: str
    earnings_date: str
    prediction: str  # 'beat', 'miss', 'meet'
    sentiment: str   # 'bullish', 'bearish', 'neutral'
    was_contrarian: bool
    was_correct: bool
    actual_result: str
    date_analyzed: str
    headline: str
    url: str

class SimplifiedContrarianAnalyzer:
    def __init__(self):
        load_dotenv()
        self.guardian_api_key = os.getenv("GUARDIAN_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.guardian_api_key:
            raise ValueError("GUARDIAN_API_KEY not found in environment variables")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.groq_client = Groq(api_key=self.groq_api_key)
        
        # Database paths
        self.database_dir = "simplified_contrarian_db"
        self.records_file = os.path.join(self.database_dir, "contrarian_records.csv")
        self.author_stats_file = os.path.join(self.database_dir, "author_statistics.csv")
        
        # Create database directory
        os.makedirs(self.database_dir, exist_ok=True)
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize CSV files if they don't exist"""
        # Initialize records file
        if not os.path.exists(self.records_file):
            headers = [
                'author', 'company', 'symbol', 'earnings_date', 'prediction',
                'sentiment', 'was_contrarian', 'was_correct', 'actual_result',
                'date_analyzed', 'headline', 'url'
            ]
            with open(self.records_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
        
        # Initialize author stats file
        if not os.path.exists(self.author_stats_file):
            headers = [
                'author', 'total_predictions', 'contrarian_predictions',
                'correct_predictions', 'correct_contrarian_predictions',
                'overall_accuracy', 'contrarian_accuracy', 'last_updated',
                'recent_streak', 'companies_covered', 'specialization'
            ]
            with open(self.author_stats_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
    
    def collect_pre_earnings_articles(self, company_name: str, earnings_date: str, days_before: int = 30) -> List[Dict]:
        """Collect articles from Guardian API before earnings date"""
        try:
            earnings_dt = datetime.strptime(earnings_date, '%Y-%m-%d')
            from_date = earnings_dt - timedelta(days=days_before)
            to_date = earnings_dt - timedelta(days=1)
            
            url = "https://content.guardianapis.com/search"
            params = {
                'api-key': self.guardian_api_key,
                'q': company_name,
                'from-date': from_date.strftime('%Y-%m-%d'),
                'to-date': to_date.strftime('%Y-%m-%d'),
                'show-fields': 'headline,byline,wordcount,body',
                'show-tags': 'contributor',
                'page-size': 50,
                'order-by': 'relevance'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data['response']['results']:
                # Extract author from byline or tags
                author = 'Unknown'
                if item.get('fields', {}).get('byline'):
                    author = item['fields']['byline']
                elif item.get('tags'):
                    contributors = [tag['webTitle'] for tag in item['tags'] if tag['type'] == 'contributor']
                    if contributors:
                        author = contributors[0]
                
                articles.append({
                    'headline': item.get('webTitle', ''),
                    'author': author,
                    'date': item.get('webPublicationDate', ''),
                    'url': item.get('webUrl', ''),
                    'body': item.get('fields', {}).get('body', ''),
                    'word_count': item.get('fields', {}).get('wordcount', 0)
                })
            
            logger.info(f"Collected {len(articles)} articles for {company_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error collecting articles: {e}")
            return []
    
    def analyze_article_sentiment_and_prediction(self, article: Dict) -> Optional[Dict]:
        """Analyze article for sentiment and earnings prediction using Groq"""
        try:
            time.sleep(random.uniform(1, 3))  # Rate limiting
            
            prompt = f"""
            Analyze this financial article and provide a simple classification:
            
            Headline: {article['headline']}
            Content: {article['body'][:2000]}...
            
            Please respond with ONLY a JSON object containing:
            {{
                "sentiment": "bullish" | "bearish" | "neutral",
                "earnings_prediction": "beat" | "miss" | "meet",
                "confidence": "high" | "medium" | "low",
                "reasoning": "brief explanation"
            }}
            
            Focus on:
            - Overall sentiment about the company's prospects
            - Implied prediction about upcoming earnings
            - Keep it simple and clear
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if '{' in content and '}' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                return json.loads(json_str)
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return None
    
    def get_actual_earnings_result(self, company_symbol: str, earnings_date: str) -> Optional[Dict]:
        """Get actual earnings result using stock price movement"""
        try:
            ticker = yf.Ticker(company_symbol)
            earnings_dt = datetime.strptime(earnings_date, '%Y-%m-%d')
            
            # Get price data around earnings
            start_date = earnings_dt - timedelta(days=5)
            end_date = earnings_dt + timedelta(days=5)
            
            hist = ticker.history(start=start_date, end=end_date)
            
            if len(hist) >= 2:
                # Find the closest trading day to earnings
                earnings_price_idx = None
                min_diff = float('inf')
                
                for i, date in enumerate(hist.index):
                    diff = abs((date.date() - earnings_dt.date()).days)
                    if diff < min_diff:
                        min_diff = diff
                        earnings_price_idx = i
                
                if earnings_price_idx is not None and earnings_price_idx > 0:
                    pre_earnings_price = hist['Close'].iloc[earnings_price_idx - 1]
                    post_earnings_price = hist['Close'].iloc[earnings_price_idx]
                    price_change = ((post_earnings_price - pre_earnings_price) / pre_earnings_price) * 100
                    
                    # Simple classification based on price movement
                    if price_change > 3:
                        result = 'beat'
                    elif price_change < -3:
                        result = 'miss'
                    else:
                        result = 'meet'
                    
                    return {
                        'result': result,
                        'price_change_percent': round(price_change, 2),
                        'pre_earnings_price': round(pre_earnings_price, 2),
                        'post_earnings_price': round(post_earnings_price, 2)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting earnings result: {e}")
            return None
    
    def identify_contrarians(self, analyzed_articles: List[Dict], actual_result: Optional[Dict]) -> List[ContrarianRecord]:
        """Identify contrarian voices with simple logic"""
        valid_articles = [article for article in analyzed_articles if article.get('analysis')]
        
        if not valid_articles:
            return []
        
        # Count consensus
        sentiment_counts = Counter([article['analysis']['sentiment'] for article in valid_articles])
        prediction_counts = Counter([article['analysis']['earnings_prediction'] for article in valid_articles])
        
        # Determine consensus (most common view)
        consensus_sentiment = sentiment_counts.most_common(1)[0][0]
        consensus_prediction = prediction_counts.most_common(1)[0][0]
        
        logger.info(f"Consensus sentiment: {consensus_sentiment}")
        logger.info(f"Consensus prediction: {consensus_prediction}")
        
        contrarian_records = []
        
        for article in valid_articles:
            analysis = article['analysis']
            
            # Simple contrarian identification
            is_contrarian = (
                analysis['sentiment'] != consensus_sentiment or 
                analysis['earnings_prediction'] != consensus_prediction
            )
            
            # Check if prediction was correct
            was_correct = False
            if actual_result:
                prediction_correct = analysis['earnings_prediction'] == actual_result['result']
                
                # Map price change to sentiment
                if actual_result['price_change_percent'] > 3:
                    actual_sentiment = 'bullish'
                elif actual_result['price_change_percent'] < -3:
                    actual_sentiment = 'bearish'
                else:
                    actual_sentiment = 'neutral'
                
                sentiment_correct = analysis['sentiment'] == actual_sentiment
                was_correct = prediction_correct or sentiment_correct
            
            record = ContrarianRecord(
                author=article['author'],
                company=article.get('company', ''),
                symbol=article.get('symbol', ''),
                earnings_date=article.get('earnings_date', ''),
                prediction=analysis['earnings_prediction'],
                sentiment=analysis['sentiment'],
                was_contrarian=is_contrarian,
                was_correct=was_correct,
                actual_result=actual_result['result'] if actual_result else 'unknown',
                date_analyzed=datetime.now().strftime('%Y-%m-%d'),
                headline=article['headline'],
                url=article['url']
            )
            
            contrarian_records.append(record)
        
        return contrarian_records
    
    def save_records(self, records: List[ContrarianRecord]):
        """Save contrarian records to CSV"""
        with open(self.records_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for record in records:
                writer.writerow([
                    record.author, record.company, record.symbol, record.earnings_date,
                    record.prediction, record.sentiment, record.was_contrarian,
                    record.was_correct, record.actual_result, record.date_analyzed,
                    record.headline, record.url
                ])
        
        logger.info(f"Saved {len(records)} records to database")
    
    def update_author_statistics(self):
        """Update author statistics based on all records"""
        # Load all records
        df = pd.read_csv(self.records_file)
        
        author_stats = {}
        
        for author in df['author'].unique():
            author_records = df[df['author'] == author]
            
            total_predictions = len(author_records)
            contrarian_predictions = len(author_records[author_records['was_contrarian'] == True])
            correct_predictions = len(author_records[author_records['was_correct'] == True])
            correct_contrarian = len(author_records[
                (author_records['was_contrarian'] == True) & 
                (author_records['was_correct'] == True)
            ])
            
            overall_accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
            contrarian_accuracy = (correct_contrarian / contrarian_predictions * 100) if contrarian_predictions > 0 else 0
            
            # Calculate recent streak (last 5 predictions)
            recent_records = author_records.tail(5)
            recent_streak = len(recent_records[recent_records['was_correct'] == True])
            
            companies_covered = author_records['company'].nunique()
            
            # Determine specialization
            if companies_covered == 1:
                specialization = author_records['company'].iloc[0]
            elif companies_covered <= 3:
                specialization = 'focused'
            else:
                specialization = 'generalist'
            
            author_stats[author] = {
                'author': author,
                'total_predictions': total_predictions,
                'contrarian_predictions': contrarian_predictions,
                'correct_predictions': correct_predictions,
                'correct_contrarian_predictions': correct_contrarian,
                'overall_accuracy': round(overall_accuracy, 1),
                'contrarian_accuracy': round(contrarian_accuracy, 1),
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'recent_streak': recent_streak,
                'companies_covered': companies_covered,
                'specialization': specialization
            }
        
        # Save to CSV
        with open(self.author_stats_file, 'w', newline='', encoding='utf-8') as f:
            if author_stats:
                fieldnames = list(author_stats[list(author_stats.keys())[0]].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for stats in author_stats.values():
                    writer.writerow(stats)
        
        logger.info(f"Updated statistics for {len(author_stats)} authors")
    
    def get_investment_signals(self, company_symbol: str) -> Dict:
        """Generate simple investment signals based on contrarian analysis"""
        df = pd.read_csv(self.author_stats_file)
        
        # Find authors with high contrarian accuracy (>60%) and recent activity
        reliable_contrarians = df[
            (df['contrarian_accuracy'] > 60) & 
            (df['contrarian_predictions'] >= 3)
        ].sort_values('contrarian_accuracy', ascending=False)
        
        signals = {
            'reliable_contrarians_count': len(reliable_contrarians),
            'top_contrarians': reliable_contrarians.head(5)[['author', 'contrarian_accuracy', 'contrarian_predictions']].to_dict('records'),
            'recommendation': 'MONITOR',
            'confidence': 'LOW'
        }
        
        if len(reliable_contrarians) >= 3:
            signals['recommendation'] = 'CONSIDER'
            signals['confidence'] = 'MEDIUM'
        
        if len(reliable_contrarians) >= 5:
            signals['recommendation'] = 'STRONG_SIGNAL'
            signals['confidence'] = 'HIGH'
        
        return signals
    
    def analyze_company_earnings(self, company_name: str, company_symbol: str, earnings_date: str, days_before: int = 30) -> Dict:
        """Main analysis function with simplified approach"""
        logger.info(f"Starting simplified contrarian analysis for {company_name} ({company_symbol})")
        
        # Step 1: Collect articles
        articles = self.collect_pre_earnings_articles(company_name, earnings_date, days_before)
        
        if not articles:
            return {'error': 'No articles found'}
        
        # Step 2: Analyze articles
        analyzed_articles = []
        for article in articles[:20]:  # Limit to 20 articles for simplicity
            analysis = self.analyze_article_sentiment_and_prediction(article)
            if analysis:
                analyzed_articles.append({
                    **article,
                    'analysis': analysis,
                    'company': company_name,
                    'symbol': company_symbol,
                    'earnings_date': earnings_date
                })
        
        # Step 3: Get actual results
        actual_result = self.get_actual_earnings_result(company_symbol, earnings_date)
        
        # Step 4: Identify contrarians
        contrarian_records = self.identify_contrarians(analyzed_articles, actual_result)
        
        # Step 5: Save to database
        self.save_records(contrarian_records)
        self.update_author_statistics()
        
        # Step 6: Generate signals
        investment_signals = self.get_investment_signals(company_symbol)
        
        # Generate simple report
        contrarians_found = [r for r in contrarian_records if r.was_contrarian]
        correct_contrarians = [r for r in contrarians_found if r.was_correct]
        
        report = {
            'company': company_name,
            'symbol': company_symbol,
            'earnings_date': earnings_date,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'summary': {
                'total_articles_analyzed': len(analyzed_articles),
                'contrarians_identified': len(contrarians_found),
                'correct_contrarians': len(correct_contrarians),
                'contrarian_accuracy': round((len(correct_contrarians) / len(contrarians_found) * 100), 1) if contrarians_found else 0
            },
            'actual_result': actual_result,
            'contrarian_authors': [{
                'author': r.author,
                'prediction': r.prediction,
                'sentiment': r.sentiment,
                'was_correct': r.was_correct,
                'headline': r.headline
            } for r in contrarians_found],
            'investment_signals': investment_signals
        }
        
        return report

if __name__ == "__main__":
    # Example usage
    analyzer = SimplifiedContrarianAnalyzer()
    
    # Test with Apple earnings
    result = analyzer.analyze_company_earnings(
        company_name="Apple",
        company_symbol="AAPL",
        earnings_date="2024-11-01",
        days_before=30
    )
    
    print(json.dumps(result, indent=2))