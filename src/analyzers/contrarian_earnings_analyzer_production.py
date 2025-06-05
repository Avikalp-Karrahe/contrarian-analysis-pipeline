#!/usr/bin/env python3
"""
Production Contrarian Earnings Analyzer

This system identifies contrarian analysts/authors who were minority voices before earnings
but were proven right when actual earnings results were released.

Key improvements:
- Rate limiting for API calls
- Better error handling
- Configurable parameters
- Multiple data sources
- Production-ready logging
- Batch processing with delays
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
from .contrarian_csv_exporter import ContrarianCSVExporter

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('contrarian_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuration for API rate limiting"""
    guardian_requests_per_minute: int = 12  # Guardian API free tier: 12 requests/minute
    groq_requests_per_minute: int = 30      # Groq free tier: 30 requests/minute
    min_delay_between_requests: float = 1.0  # Minimum delay between requests
    max_delay_between_requests: float = 3.0  # Maximum delay for jitter

class ProductionContrarianEarningsAnalyzer:
    def __init__(self, rate_limit_config: Optional[RateLimitConfig] = None):
        load_dotenv()
        self.guardian_api_key = os.getenv("GUARDIAN_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.guardian_api_key:
            raise ValueError("GUARDIAN_API_KEY not found in environment variables")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.groq_client = Groq(api_key=self.groq_api_key)
        self.rate_limit = rate_limit_config or RateLimitConfig()
        
        # Track API usage
        self.guardian_requests_count = 0
        self.groq_requests_count = 0
        self.last_guardian_request = 0
        self.last_groq_request = 0
        
    def _wait_for_rate_limit(self, api_type: str):
        """Implement rate limiting with jitter"""
        current_time = time.time()
        
        if api_type == "guardian":
            time_since_last = current_time - self.last_guardian_request
            min_interval = 60 / self.rate_limit.guardian_requests_per_minute
        elif api_type == "groq":
            time_since_last = current_time - self.last_groq_request
            min_interval = 60 / self.rate_limit.groq_requests_per_minute
        else:
            min_interval = self.rate_limit.min_delay_between_requests
            time_since_last = 0
            
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            # Add jitter to avoid thundering herd
            jitter = random.uniform(0, min(1.0, sleep_time * 0.1))
            total_sleep = sleep_time + jitter
            logger.info(f"Rate limiting: sleeping for {total_sleep:.2f} seconds")
            time.sleep(total_sleep)
            
        # Add random delay between requests
        delay = random.uniform(
            self.rate_limit.min_delay_between_requests,
            self.rate_limit.max_delay_between_requests
        )
        time.sleep(delay)
        
    def collect_pre_earnings_articles(self, company_name: str, earnings_date: str, days_before: int = 30) -> List[Dict]:
        """
        Collect articles about the company published before earnings date with rate limiting
        """
        logger.info(f"Collecting articles for {company_name} before {earnings_date} ({days_before} days)")
        
        # Calculate date range
        earnings_dt = datetime.strptime(earnings_date, "%Y-%m-%d")
        start_date = earnings_dt - timedelta(days=days_before)
        end_date = earnings_dt - timedelta(days=1)  # Day before earnings
        
        logger.info(f"Search date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        articles = []
        page = 1
        max_pages = 10  # Increased for 30-day period
        
        while page <= max_pages:
            try:
                # Rate limiting
                self._wait_for_rate_limit("guardian")
                
                logger.info(f"Fetching page {page}/{max_pages}")
                
                response = requests.get("https://content.guardianapis.com/search", params={
                    "api-key": self.guardian_api_key,
                    "q": company_name,
                    "from-date": start_date.strftime("%Y-%m-%d"),
                    "to-date": end_date.strftime("%Y-%m-%d"),
                    "page-size": 50,
                    "page": page,
                    "show-fields": "all",
                    "order-by": "newest",
                    "section": "business|technology|money"  # Focus on relevant sections
                })
                
                self.last_guardian_request = time.time()
                self.guardian_requests_count += 1
                
                if response.status_code == 429:  # Rate limit exceeded
                    logger.warning("Rate limit exceeded, waiting longer...")
                    time.sleep(60)  # Wait 1 minute
                    continue
                    
                if response.status_code != 200:
                    logger.error(f"API request failed: {response.status_code} - {response.text}")
                    break
                    
                data = response.json()
                
                if 'response' not in data or 'results' not in data['response']:
                    logger.error("Unexpected API response structure")
                    break
                    
                results = data['response']['results']
                if not results:
                    logger.info(f"No more results found on page {page}")
                    break
                    
                page_articles = 0
                for article in results:
                    if 'fields' in article and article['fields'].get('bodyText'):
                        # Filter for substantial articles
                        body_text = article['fields'].get('bodyText', '')
                        if len(body_text) > 200:  # Only articles with substantial content
                            articles.append({
                                'headline': article['fields'].get('headline', ''),
                                'body': body_text,
                                'author': article['fields'].get('byline', 'Unknown'),
                                'date': article['fields'].get('firstPublicationDate', ''),
                                'url': article['fields'].get('shortUrl', ''),
                                'trail_text': article['fields'].get('trailText', ''),
                                'section': article.get('sectionName', ''),
                                'word_count': len(body_text.split())
                            })
                            page_articles += 1
                
                logger.info(f"Page {page}: Found {page_articles} relevant articles")
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
                
        logger.info(f"Total articles collected: {len(articles)}")
        
        # Sort by date (newest first) and word count (longer articles first)
        articles.sort(key=lambda x: (x['date'], x['word_count']), reverse=True)
        
        return articles
    
    def analyze_article_sentiment_and_prediction(self, article: Dict) -> Optional[Dict]:
        """
        Analyze each article with rate limiting and better error handling
        """
        try:
            # Rate limiting for Groq API
            self._wait_for_rate_limit("groq")
            
            # Truncate content to avoid token limits
            content = article['body'][:3000]  # Increased limit for better analysis
            
            prompt = f"""
            Analyze this financial article about {article.get('headline', 'earnings expectations')}:
            
            Headline: {article['headline']}
            Author: {article['author']}
            Date: {article['date']}
            Section: {article.get('section', 'N/A')}
            Content: {content}...
            
            Provide analysis in JSON format:
            {{
                "sentiment": "bullish/bearish/neutral",
                "confidence": "high/medium/low",
                "earnings_prediction": "beat/miss/meet/unclear",
                "specific_predictions": ["list of specific predictions made"],
                "reasoning": "brief explanation of the analysis",
                "key_concerns": ["main concerns or positive points mentioned"],
                "prediction_confidence": "high/medium/low",
                "financial_metrics_mentioned": ["revenue", "profit", "eps", etc.],
                "contrarian_indicators": ["signs this might be a contrarian view"]
            }}
            
            Focus on:
            - Overall tone about company prospects before earnings
            - Specific earnings predictions or expectations
            - Revenue/profit forecasts
            - Any contrarian viewpoints expressed
            - Confidence level of predictions
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a financial analyst expert at analyzing earnings predictions and sentiment in financial articles. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.1,
                max_tokens=1000
            )
            
            self.last_groq_request = time.time()
            self.groq_requests_count += 1
            
            analysis_text = response.choices[0].message.content
            
            # Extract JSON from response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = analysis_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['sentiment', 'earnings_prediction', 'confidence']
                for field in required_fields:
                    if field not in analysis:
                        logger.warning(f"Missing required field {field} in analysis")
                        analysis[field] = 'unclear'
                        
                return analysis
            else:
                logger.error("Could not extract JSON from LLM response")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return None
    
    def get_actual_earnings_result(self, company_symbol: str, earnings_date: str) -> Optional[Dict]:
        """
        Get actual earnings results with better error handling
        """
        try:
            logger.info(f"Fetching actual earnings data for {company_symbol} around {earnings_date}")
            
            ticker = yf.Ticker(company_symbol)
            earnings_dt = datetime.strptime(earnings_date, "%Y-%m-%d")
            
            # Get stock price movement around earnings (more reliable than earnings data)
            start_date = earnings_dt - timedelta(days=5)
            end_date = earnings_dt + timedelta(days=5)
            
            hist = ticker.history(start=start_date, end=end_date)
            
            if len(hist) >= 2:
                # Find the closest trading day to earnings date
                earnings_price_idx = hist.index.get_indexer([earnings_dt], method='nearest')[0]
                
                if earnings_price_idx > 0:
                    pre_earnings_price = hist['Close'].iloc[earnings_price_idx - 1]
                    post_earnings_price = hist['Close'].iloc[min(earnings_price_idx + 1, len(hist) - 1)]
                    
                    price_change = ((post_earnings_price - pre_earnings_price) / pre_earnings_price) * 100
                    
                    # Get additional context
                    volume_change = 0
                    if earnings_price_idx < len(hist) - 1:
                        avg_volume_before = hist['Volume'].iloc[:earnings_price_idx].mean()
                        volume_after = hist['Volume'].iloc[earnings_price_idx]
                        volume_change = ((volume_after - avg_volume_before) / avg_volume_before) * 100
                    
                    # Determine result based on price movement
                    if price_change > 3:
                        result = 'beat'
                    elif price_change < -3:
                        result = 'miss'
                    else:
                        result = 'meet'
                    
                    return {
                        'earnings_date': earnings_date,
                        'actual_date_used': hist.index[earnings_price_idx].strftime('%Y-%m-%d'),
                        'pre_earnings_price': round(pre_earnings_price, 2),
                        'post_earnings_price': round(post_earnings_price, 2),
                        'price_change_percent': round(price_change, 2),
                        'volume_change_percent': round(volume_change, 2),
                        'result': result,
                        'data_source': 'yfinance_price_movement'
                    }
            
            logger.warning(f"Insufficient price data for {company_symbol} around {earnings_date}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting earnings data: {e}")
            return None
    
    def identify_contrarians(self, analyzed_articles: List[Dict], actual_result: Optional[Dict]) -> List[Dict]:
        """
        Identify contrarian voices with improved scoring
        """
        valid_articles = [article for article in analyzed_articles if article.get('analysis')]
        
        if not valid_articles:
            logger.warning("No valid analyzed articles found")
            return []
        
        # Count distributions
        sentiment_counts = Counter([article['analysis']['sentiment'] for article in valid_articles])
        prediction_counts = Counter([article['analysis']['earnings_prediction'] for article in valid_articles])
        
        total_articles = len(valid_articles)
        
        logger.info(f"Sentiment distribution: {dict(sentiment_counts)}")
        logger.info(f"Prediction distribution: {dict(prediction_counts)}")
        logger.info(f"Actual result: {actual_result}")
        
        contrarians = []
        
        for article in valid_articles:
            analysis = article['analysis']
            
            author_sentiment = analysis['sentiment']
            author_prediction = analysis['earnings_prediction']
            
            # Calculate minority status (threshold: less than 40% of total)
            sentiment_percentage = sentiment_counts[author_sentiment] / total_articles
            prediction_percentage = prediction_counts[author_prediction] / total_articles
            
            is_minority_sentiment = sentiment_percentage < 0.4
            is_minority_prediction = prediction_percentage < 0.4
            
            # Check correctness against actual results
            was_correct = False
            sentiment_correct = False
            prediction_correct = False
            
            if actual_result:
                # Map actual result to sentiment
                if actual_result['price_change_percent'] > 3:
                    actual_sentiment = 'bullish'
                elif actual_result['price_change_percent'] < -3:
                    actual_sentiment = 'bearish'
                else:
                    actual_sentiment = 'neutral'
                
                sentiment_correct = author_sentiment == actual_sentiment
                prediction_correct = author_prediction == actual_result['result']
                was_correct = sentiment_correct or prediction_correct
            
            # Calculate contrarian score
            # Include contrarians based on minority views (with or without actual results)
            if is_minority_sentiment or is_minority_prediction:
                contrarian_score = 0
                
                # Score based on how minority the view was
                if is_minority_sentiment:
                    minority_factor = (1 - sentiment_percentage) * 100
                    confidence_bonus = 20 if analysis.get('confidence') == 'high' else 10 if analysis.get('confidence') == 'medium' else 5
                    base_score = minority_factor + confidence_bonus
                    
                    # Bonus if correct (when actual results available)
                    if actual_result and sentiment_correct:
                        base_score *= 1.5  # 50% bonus for being correct
                    
                    contrarian_score += base_score
                    
                if is_minority_prediction:
                    minority_factor = (1 - prediction_percentage) * 100
                    confidence_bonus = 20 if analysis.get('prediction_confidence') == 'high' else 10 if analysis.get('prediction_confidence') == 'medium' else 5
                    base_score = minority_factor + confidence_bonus
                    
                    # Bonus if correct (when actual results available)
                    if actual_result and prediction_correct:
                        base_score *= 1.5  # 50% bonus for being correct
                    
                    contrarian_score += base_score
                
                contrarians.append({
                    'author': article['author'],
                    'headline': article['headline'],
                    'date': article['date'],
                    'url': article['url'],
                    'section': article.get('section', 'N/A'),
                    'word_count': article.get('word_count', 0),
                    'sentiment': author_sentiment,
                    'prediction': author_prediction,
                    'sentiment_percentage': round(sentiment_percentage * 100, 1),
                    'prediction_percentage': round(prediction_percentage * 100, 1),
                    'was_minority_sentiment': is_minority_sentiment,
                    'was_minority_prediction': is_minority_prediction,
                    'sentiment_correct': sentiment_correct,
                    'prediction_correct': prediction_correct,
                    'contrarian_score': round(contrarian_score, 2),
                    'reasoning': analysis.get('reasoning', ''),
                    'key_concerns': analysis.get('key_concerns', []),
                    'confidence': analysis.get('confidence', 'unknown'),
                    'prediction_confidence': analysis.get('prediction_confidence', 'unknown'),
                    'contrarian_indicators': analysis.get('contrarian_indicators', []),
                    'actual_result_available': actual_result is not None
                })
        
        # Sort by contrarian score
        contrarians.sort(key=lambda x: x['contrarian_score'], reverse=True)
        
        logger.info(f"Identified {len(contrarians)} contrarian voices")
        
        return contrarians
    
    def analyze_company_earnings(self, company_name: str, company_symbol: str, earnings_date: str, days_before: int = 30, max_articles: int = 50) -> Optional[Dict]:
        """
        Main analysis function with production-ready features
        """
        start_time = time.time()
        logger.info(f"Starting contrarian analysis for {company_name} ({company_symbol}) - Earnings: {earnings_date}")
        logger.info(f"Analysis parameters: {days_before} days before, max {max_articles} articles")
        
        try:
            # Step 1: Collect pre-earnings articles
            articles = self.collect_pre_earnings_articles(company_name, earnings_date, days_before)
            
            if not articles:
                logger.error("No articles found")
                return None
            
            # Limit articles for analysis (prioritize recent and substantial)
            articles_to_analyze = articles[:max_articles]
            logger.info(f"Analyzing top {len(articles_to_analyze)} articles out of {len(articles)} found")
            
            # Step 2: Analyze each article with progress tracking
            analyzed_articles = []
            failed_analyses = 0
            
            for i, article in enumerate(articles_to_analyze):
                logger.info(f"Analyzing article {i+1}/{len(articles_to_analyze)}: {article['headline'][:50]}...")
                
                analysis = self.analyze_article_sentiment_and_prediction(article)
                
                analyzed_articles.append({
                    **article,
                    'analysis': analysis
                })
                
                if analysis is None:
                    failed_analyses += 1
                    
                # Progress update every 10 articles
                if (i + 1) % 10 == 0:
                    success_rate = ((i + 1 - failed_analyses) / (i + 1)) * 100
                    logger.info(f"Progress: {i+1}/{len(articles_to_analyze)} articles analyzed (Success rate: {success_rate:.1f}%)")
            
            logger.info(f"Article analysis complete. Success rate: {((len(articles_to_analyze) - failed_analyses) / len(articles_to_analyze)) * 100:.1f}%")
            
            # Step 3: Get actual earnings results
            actual_result = self.get_actual_earnings_result(company_symbol, earnings_date)
            
            # Step 4: Identify contrarians
            contrarians = self.identify_contrarians(analyzed_articles, actual_result)
            
            # Step 5: Generate comprehensive report
            analysis_time = time.time() - start_time
            
            report = {
                'company': company_name,
                'symbol': company_symbol,
                'earnings_date': earnings_date,
                'analysis_date': datetime.now().isoformat(),
                'analysis_parameters': {
                    'days_before_earnings': days_before,
                    'max_articles_analyzed': max_articles,
                    'analysis_duration_seconds': round(analysis_time, 2)
                },
                'data_collection': {
                    'total_articles_found': len(articles),
                    'articles_analyzed': len(articles_to_analyze),
                    'successful_analyses': len(articles_to_analyze) - failed_analyses,
                    'failed_analyses': failed_analyses
                },
                'api_usage': {
                    'guardian_requests': self.guardian_requests_count,
                    'groq_requests': self.groq_requests_count
                },
                'actual_result': actual_result,
                'contrarians_found': len(contrarians),
                'contrarian_analysts': contrarians,
                'analyzed_articles': analyzed_articles,
                'summary': {
                    'top_contrarian': contrarians[0] if contrarians else None,
                    'avg_contrarian_score': round(sum(c['contrarian_score'] for c in contrarians) / len(contrarians), 2) if contrarians else 0,
                    'sentiment_distribution': dict(Counter([a['analysis']['sentiment'] for a in analyzed_articles if a['analysis']])),
                    'prediction_distribution': dict(Counter([a['analysis']['earnings_prediction'] for a in analyzed_articles if a['analysis']]))
                }
            }
            
            logger.info(f"Analysis completed in {analysis_time:.2f} seconds")
            return report
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return None
    
    def save_report(self, report: Dict, filename: Optional[str] = None) -> str:
        """
        Save the contrarian analysis report with backup
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"contrarian_analysis_{report['symbol']}_{timestamp}.json"
        
        # Get the project root directory (two levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Save to reports directory
        reports_dir = os.path.join(project_root, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)
        
        # Also save to outputs directory for easy access
        outputs_dir = os.path.join(project_root, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        outputs_filepath = os.path.join(outputs_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            with open(outputs_filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Report saved to {filepath} and {outputs_filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return ""

def main():
    """
    Production example usage
    """
    # Initialize analyzer with rate limiting
    rate_config = RateLimitConfig(
        guardian_requests_per_minute=10,  # Conservative rate
        groq_requests_per_minute=25,     # Conservative rate
        min_delay_between_requests=1.5,
        max_delay_between_requests=3.0
    )
    
    analyzer = ProductionContrarianEarningsAnalyzer(rate_config)
    
    # Example: Analyze recent earnings
    company_name = "Apple"
    company_symbol = "AAPL"
    earnings_date = "2024-11-01"  # Use a past date for testing
    
    print(f"Starting production contrarian analysis for {company_name} earnings on {earnings_date}")
    print(f"This will analyze articles from 30 days before the earnings date...")
    print(f"Rate limiting: Guardian API max {rate_config.guardian_requests_per_minute}/min, Groq API max {rate_config.groq_requests_per_minute}/min")
    
    report = analyzer.analyze_company_earnings(
        company_name=company_name,
        company_symbol=company_symbol,
        earnings_date=earnings_date,
        days_before=30,
        max_articles=30  # Reasonable limit for free APIs
    )
    
    if report:
        # Save report
        filepath = analyzer.save_report(report)
        
        # Export to CSV
        csv_exporter = ContrarianCSVExporter()
        
        print("\nExporting data to CSV files...")
        exported_csv_files = csv_exporter.export_full_analysis(report)
        
        # Print comprehensive summary
        print("\n" + "="*60)
        print("PRODUCTION CONTRARIAN ANALYSIS SUMMARY")
        print("="*60)
        print(f"Company: {report['company']} ({report['symbol']})")
        print(f"Earnings Date: {report['earnings_date']}")
        print(f"Analysis Duration: {report['analysis_parameters']['analysis_duration_seconds']} seconds")
        print(f"Articles Found: {report['data_collection']['total_articles_found']}")
        print(f"Articles Analyzed: {report['data_collection']['articles_analyzed']}")
        print(f"Successful Analyses: {report['data_collection']['successful_analyses']}")
        print(f"API Requests - Guardian: {report['api_usage']['guardian_requests']}, Groq: {report['api_usage']['groq_requests']}")
        
        if report['actual_result']:
            print(f"\nACTUAL EARNINGS RESULT:")
            print(f"Price Change: {report['actual_result']['price_change_percent']}%")
            print(f"Result: {report['actual_result']['result'].upper()}")
            print(f"Volume Change: {report['actual_result']['volume_change_percent']}%")
        
        print(f"\nCONTRARIANS FOUND: {report['contrarians_found']}")
        
        if report['contrarian_analysts']:
            print("\nTOP 3 CONTRARIANS:")
            for i, contrarian in enumerate(report['contrarian_analysts'][:3], 1):
                print(f"\n{i}. {contrarian['author']}")
                print(f"   Headline: {contrarian['headline'][:80]}...")
                print(f"   Score: {contrarian['contrarian_score']}")
                print(f"   Sentiment: {contrarian['sentiment']} ({contrarian['sentiment_percentage']}% of articles)")
                print(f"   Prediction: {contrarian['prediction']} ({contrarian['prediction_percentage']}% of articles)")
                print(f"   Correct: Sentiment={contrarian['sentiment_correct']}, Prediction={contrarian['prediction_correct']}")
        
        print(f"\nSENTIMENT DISTRIBUTION: {report['summary']['sentiment_distribution']}")
        print(f"PREDICTION DISTRIBUTION: {report['summary']['prediction_distribution']}")
        print(f"\nFull report saved to: {filepath}")
        
    else:
        print("Analysis failed. Check logs for details.")

if __name__ == "__main__":
    main()