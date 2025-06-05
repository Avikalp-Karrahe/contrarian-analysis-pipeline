#!/usr/bin/env python3
"""
Contrarian Earnings Analyzer

This system identifies contrarian analysts/authors who were minority voices before earnings
but were proven right when actual earnings results were released.

Workflow:
1. Take company name and earnings date as input
2. Search for articles published before earnings date
3. Analyze sentiment and predictions from each article/author
4. Compare predictions with actual earnings results
5. Identify contrarian voices who were minority but correct
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContrarianEarningsAnalyzer:
    def __init__(self):
        load_dotenv()
        self.guardian_api_key = os.getenv("GUARDIAN_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_api_key)
        
    def collect_pre_earnings_articles(self, company_name, earnings_date, days_before=30):
        """
        Collect articles about the company published before earnings date
        """
        logger.info(f"Collecting articles for {company_name} before {earnings_date}")
        
        # Calculate date range
        earnings_dt = datetime.strptime(earnings_date, "%Y-%m-%d")
        start_date = earnings_dt - timedelta(days=days_before)
        end_date = earnings_dt - timedelta(days=1)  # Day before earnings
        
        # Search Guardian API
        articles = []
        page = 1
        
        while page <= 5:  # Limit to 5 pages
            response = requests.get("https://content.guardianapis.com/search", params={
                "api-key": self.guardian_api_key,
                "q": company_name,
                "from-date": start_date.strftime("%Y-%m-%d"),
                "to-date": end_date.strftime("%Y-%m-%d"),
                "page-size": 50,
                "page": page,
                "show-fields": "all",
                "order-by": "newest"
            })
            
            if response.status_code != 200:
                logger.error(f"API request failed: {response.status_code}")
                break
                
            data = response.json()
            
            if 'response' not in data or 'results' not in data['response']:
                logger.error("Unexpected API response structure")
                break
                
            results = data['response']['results']
            if not results:
                break
                
            for article in results:
                if 'fields' in article:
                    articles.append({
                        'headline': article['fields'].get('headline', ''),
                        'body': article['fields'].get('bodyText', ''),
                        'author': article['fields'].get('byline', 'Unknown'),
                        'date': article['fields'].get('firstPublicationDate', ''),
                        'url': article['fields'].get('shortUrl', ''),
                        'trail_text': article['fields'].get('trailText', '')
                    })
            
            page += 1
            
        logger.info(f"Collected {len(articles)} articles")
        return articles
    
    def analyze_article_sentiment_and_prediction(self, article):
        """
        Analyze each article for:
        1. Sentiment (bullish/bearish/neutral)
        2. Specific earnings predictions
        3. Confidence level
        """
        prompt = f"""
        Analyze this financial article about earnings expectations:
        
        Headline: {article['headline']}
        Author: {article['author']}
        Content: {article['body'][:2000]}...
        
        Please provide analysis in JSON format:
        {{
            "sentiment": "bullish/bearish/neutral",
            "confidence": "high/medium/low",
            "earnings_prediction": "beat/miss/meet/unclear",
            "specific_predictions": ["list of specific predictions made"],
            "reasoning": "brief explanation of the analysis",
            "key_concerns": ["main concerns or positive points mentioned"],
            "prediction_confidence": "how confident the author seems about their prediction"
        }}
        
        Focus on:
        - Overall tone about company prospects
        - Specific earnings predictions or expectations
        - Revenue/profit forecasts
        - Any contrarian viewpoints expressed
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a financial analyst expert at analyzing earnings predictions and sentiment in financial articles."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.1
            )
            
            analysis_text = response.choices[0].message.content
            # Extract JSON from response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = analysis_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                return analysis
            else:
                logger.error("Could not extract JSON from LLM response")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return None
    
    def get_actual_earnings_result(self, company_symbol, earnings_date):
        """
        Get actual earnings results using yfinance or financial APIs
        """
        try:
            ticker = yf.Ticker(company_symbol)
            
            # Get earnings data around the earnings date
            earnings_dt = datetime.strptime(earnings_date, "%Y-%m-%d")
            
            # Get quarterly earnings
            earnings = ticker.quarterly_earnings
            
            if not earnings.empty:
                # Find earnings closest to the target date
                earnings.index = pd.to_datetime(earnings.index)
                target_date = pd.to_datetime(earnings_date)
                
                # Find the closest earnings date
                closest_idx = (earnings.index - target_date).abs().idxmin()
                closest_earnings = earnings.loc[closest_idx]
                
                # Get stock price movement around earnings
                start_date = earnings_dt - timedelta(days=2)
                end_date = earnings_dt + timedelta(days=2)
                
                hist = ticker.history(start=start_date, end=end_date)
                
                if len(hist) >= 2:
                    price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
                else:
                    price_change = 0
                
                return {
                    'earnings_date': closest_idx.strftime('%Y-%m-%d'),
                    'revenue': closest_earnings.get('Revenue', 'N/A'),
                    'earnings': closest_earnings.get('Earnings', 'N/A'),
                    'price_change_percent': round(price_change, 2),
                    'result': 'beat' if price_change > 2 else 'miss' if price_change < -2 else 'meet'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting earnings data: {e}")
            return None
    
    def identify_contrarians(self, analyzed_articles, actual_result):
        """
        Identify contrarian voices who were minority but correct
        """
        # Count overall sentiment distribution
        sentiment_counts = Counter([article['analysis']['sentiment'] for article in analyzed_articles if article['analysis']])
        prediction_counts = Counter([article['analysis']['earnings_prediction'] for article in analyzed_articles if article['analysis']])
        
        total_articles = len([a for a in analyzed_articles if a['analysis']])
        
        logger.info(f"Sentiment distribution: {dict(sentiment_counts)}")
        logger.info(f"Prediction distribution: {dict(prediction_counts)}")
        logger.info(f"Actual result: {actual_result}")
        
        contrarians = []
        
        for article in analyzed_articles:
            if not article['analysis']:
                continue
                
            analysis = article['analysis']
            
            # Check if this author was contrarian
            author_sentiment = analysis['sentiment']
            author_prediction = analysis['earnings_prediction']
            
            # Determine if author was minority
            is_minority_sentiment = sentiment_counts[author_sentiment] / total_articles < 0.3
            is_minority_prediction = prediction_counts[author_prediction] / total_articles < 0.3
            
            # Check if author was correct
            was_correct = False
            
            if actual_result:
                # Check sentiment correctness
                actual_sentiment = 'bullish' if actual_result['price_change_percent'] > 2 else 'bearish' if actual_result['price_change_percent'] < -2 else 'neutral'
                sentiment_correct = author_sentiment == actual_sentiment
                
                # Check prediction correctness
                prediction_correct = author_prediction == actual_result['result']
                
                was_correct = sentiment_correct or prediction_correct
            
            # Identify contrarians
            if (is_minority_sentiment or is_minority_prediction) and was_correct:
                contrarian_score = 0
                if is_minority_sentiment and sentiment_correct:
                    contrarian_score += (1 - sentiment_counts[author_sentiment] / total_articles) * 100
                if is_minority_prediction and prediction_correct:
                    contrarian_score += (1 - prediction_counts[author_prediction] / total_articles) * 100
                
                contrarians.append({
                    'author': article['author'],
                    'headline': article['headline'],
                    'date': article['date'],
                    'url': article['url'],
                    'sentiment': author_sentiment,
                    'prediction': author_prediction,
                    'was_minority_sentiment': is_minority_sentiment,
                    'was_minority_prediction': is_minority_prediction,
                    'contrarian_score': round(contrarian_score, 2),
                    'reasoning': analysis['reasoning'],
                    'key_concerns': analysis['key_concerns']
                })
        
        # Sort by contrarian score
        contrarians.sort(key=lambda x: x['contrarian_score'], reverse=True)
        
        return contrarians
    
    def analyze_company_earnings(self, company_name, company_symbol, earnings_date):
        """
        Main analysis function
        """
        logger.info(f"Starting contrarian analysis for {company_name} ({company_symbol}) - Earnings: {earnings_date}")
        
        # Step 1: Collect pre-earnings articles
        articles = self.collect_pre_earnings_articles(company_name, earnings_date)
        
        if not articles:
            logger.error("No articles found")
            return None
        
        # Step 2: Analyze each article
        analyzed_articles = []
        for i, article in enumerate(articles[:20]):  # Limit to 20 articles for API costs
            logger.info(f"Analyzing article {i+1}/{min(20, len(articles))}")
            analysis = self.analyze_article_sentiment_and_prediction(article)
            analyzed_articles.append({
                **article,
                'analysis': analysis
            })
        
        # Step 3: Get actual earnings results
        actual_result = self.get_actual_earnings_result(company_symbol, earnings_date)
        
        # Step 4: Identify contrarians
        contrarians = self.identify_contrarians(analyzed_articles, actual_result)
        
        # Step 5: Generate report
        report = {
            'company': company_name,
            'symbol': company_symbol,
            'earnings_date': earnings_date,
            'analysis_date': datetime.now().isoformat(),
            'total_articles_analyzed': len(analyzed_articles),
            'actual_result': actual_result,
            'contrarians_found': len(contrarians),
            'contrarian_analysts': contrarians,
            'summary': {
                'top_contrarian': contrarians[0] if contrarians else None,
                'avg_contrarian_score': sum(c['contrarian_score'] for c in contrarians) / len(contrarians) if contrarians else 0
            }
        }
        
        return report
    
    def save_report(self, report, filename=None):
        """
        Save the contrarian analysis report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"contrarian_analysis_{report['symbol']}_{timestamp}.json"
        
        # Get the project root directory (two levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        reports_dir = os.path.join(project_root, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Report saved to {filepath}")
        return filepath

def main():
    """
    Example usage
    """
    analyzer = ContrarianEarningsAnalyzer()
    
    # Example: Analyze Apple's earnings
    # You can modify these parameters
    company_name = "Apple"
    company_symbol = "AAPL"
    earnings_date = "2025-05-02"  # Example date
    
    print(f"Analyzing contrarian voices for {company_name} earnings on {earnings_date}")
    
    report = analyzer.analyze_company_earnings(company_name, company_symbol, earnings_date)
    
    if report:
        # Save report
        filepath = analyzer.save_report(report)
        
        # Print summary
        print("\n" + "="*50)
        print("CONTRARIAN ANALYSIS SUMMARY")
        print("="*50)
        print(f"Company: {report['company']} ({report['symbol']})")
        print(f"Earnings Date: {report['earnings_date']}")
        print(f"Articles Analyzed: {report['total_articles_analyzed']}")
        print(f"Contrarians Found: {report['contrarians_found']}")
        
        if report['actual_result']:
            print(f"Actual Price Change: {report['actual_result']['price_change_percent']}%")
            print(f"Actual Result: {report['actual_result']['result']}")
        
        if report['contrarian_analysts']:
            print("\nTOP CONTRARIAN:")
            top = report['contrarian_analysts'][0]
            print(f"Author: {top['author']}")
            print(f"Headline: {top['headline']}")
            print(f"Contrarian Score: {top['contrarian_score']}")
            print(f"Reasoning: {top['reasoning']}")
        
        print(f"\nFull report saved to: {filepath}")
    else:
        print("Analysis failed")

if __name__ == "__main__":
    main()