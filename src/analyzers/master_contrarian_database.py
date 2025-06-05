#!/usr/bin/env python3
"""
Master Contrarian Database

This module maintains a persistent database of contrarian analysts across
multiple earnings calls and companies, tracking their historical performance
and contrarian patterns over time.
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

class MasterContrarianDatabase:
    """
    Manages a master database of contrarian analysts with historical tracking
    """
    
    def __init__(self, database_dir: str = "master_contrarian_db"):
        # Get the project root directory (two levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Use absolute path relative to project root
        if not os.path.isabs(database_dir):
            self.database_dir = os.path.join(project_root, database_dir)
        else:
            self.database_dir = database_dir
            
        self.master_csv_path = os.path.join(self.database_dir, "master_contrarian_database.csv")
        self.author_history_dir = os.path.join(self.database_dir, "author_histories")
        
        # Create directories
        os.makedirs(self.database_dir, exist_ok=True)
        os.makedirs(self.author_history_dir, exist_ok=True)
        
        # Initialize master CSV if it doesn't exist
        self._initialize_master_csv()
    
    def _initialize_master_csv(self):
        """Initialize the master CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.master_csv_path):
            headers = [
                'Author_ID',
                'Author_Name',
                'First_Seen_Date',
                'Last_Seen_Date',
                'Total_Earnings_Calls',
                'Total_Companies_Covered',
                'Total_Contrarian_Instances',
                'Successful_Contrarian_Calls',
                'Failed_Contrarian_Calls',
                'Contrarian_Success_Rate',
                'Overall_Contrarian_Score',
                'Average_Contrarian_Score_Per_Call',
                'Companies_List',
                'Latest_Company',
                'Latest_Symbol',
                'Latest_Earnings_Date',
                'Latest_Contrarian_Type',
                'Latest_Was_Correct',
                'Repeat_Contrarian_Count',
                'Consistency_Score',
                'Risk_Level',
                'Last_Updated'
            ]
            
            with open(self.master_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
            
            print(f"Initialized master contrarian database: {self.master_csv_path}")
    
    def _generate_author_id(self, author_name: str) -> str:
        """Generate a unique ID for an author"""
        # Simple ID generation - could be enhanced with more sophisticated logic
        return author_name.lower().replace(' ', '_').replace('.', '').replace(',', '')
    
    def _load_existing_data(self) -> Dict[str, Dict]:
        """Load existing contrarian data from master CSV"""
        existing_data = {}
        
        if os.path.exists(self.master_csv_path):
            try:
                df = pd.read_csv(self.master_csv_path)
                for _, row in df.iterrows():
                    author_id = row['Author_ID']
                    existing_data[author_id] = row.to_dict()
            except Exception as e:
                print(f"Error loading existing data: {e}")
        
        return existing_data
    
    def add_contrarian_analysis(self, report_data: Dict, contrarians: List[Dict]):
        """
        Add new contrarian analysis results to the master database
        """
        company = report_data.get('company', 'Unknown')
        symbol = report_data.get('symbol', 'UNK')
        earnings_date = report_data.get('earnings_date', '')
        actual_result = report_data.get('actual_result', {})
        
        # Load existing data
        existing_data = self._load_existing_data()
        updated_data = existing_data.copy()
        
        print(f"\nUpdating master contrarian database for {company} ({symbol}) - {earnings_date}")
        print(f"Found {len(contrarians)} contrarian(s) to process")
        
        for contrarian in contrarians:
            author_name = contrarian.get('author', 'Unknown')
            author_id = self._generate_author_id(author_name)
            
            # Determine if this contrarian call was correct
            was_correct = self._evaluate_contrarian_accuracy(contrarian, actual_result)
            contrarian_type = self._determine_contrarian_type(contrarian)
            contrarian_score = contrarian.get('contrarian_score', 0)
            
            if author_id in updated_data:
                # Update existing author
                author_data = updated_data[author_id]
                self._update_existing_author(author_data, company, symbol, earnings_date, 
                                           contrarian_type, was_correct, contrarian_score)
            else:
                # Add new author
                author_data = self._create_new_author_record(author_name, author_id, company, 
                                                           symbol, earnings_date, contrarian_type, 
                                                           was_correct, contrarian_score)
                updated_data[author_id] = author_data
            
            # Save individual author history
            self._save_author_history(author_id, author_name, company, symbol, 
                                    earnings_date, contrarian, was_correct)
        
        # Save updated master database
        self._save_master_database(updated_data)
        
        # Generate summary report
        self._generate_update_summary(contrarians, company, symbol, earnings_date)
    
    def _evaluate_contrarian_accuracy(self, contrarian: Dict, actual_result: Dict) -> Optional[bool]:
        """Evaluate if the contrarian's prediction was accurate"""
        if not actual_result:
            return None  # Cannot determine accuracy without actual results
        
        # Get contrarian's prediction
        prediction = contrarian.get('earnings_prediction', '').lower()
        
        # Get actual result
        actual_outcome = actual_result.get('result', '').lower()
        
        if prediction in ['beat'] and actual_outcome in ['beat']:
            return True
        elif prediction in ['miss'] and actual_outcome in ['miss']:
            return True
        elif prediction in ['meet'] and actual_outcome in ['meet']:
            return True
        elif prediction and actual_outcome:
            return False
        else:
            return None  # Unclear prediction or result
    
    def _determine_contrarian_type(self, contrarian: Dict) -> str:
        """Determine the type of contrarian call"""
        sentiment_contrarian = contrarian.get('was_minority_sentiment', False)
        prediction_contrarian = contrarian.get('was_minority_prediction', False)
        
        if sentiment_contrarian and prediction_contrarian:
            return 'Both_Sentiment_Prediction'
        elif sentiment_contrarian:
            return 'Sentiment_Only'
        elif prediction_contrarian:
            return 'Prediction_Only'
        else:
            return 'Unknown'
    
    def _update_existing_author(self, author_data: Dict, company: str, symbol: str, 
                              earnings_date: str, contrarian_type: str, 
                              was_correct: Optional[bool], contrarian_score: float):
        """Update existing author's record"""
        # Update basic counts
        author_data['Total_Earnings_Calls'] = int(author_data.get('Total_Earnings_Calls', 0)) + 1
        author_data['Total_Contrarian_Instances'] = int(author_data.get('Total_Contrarian_Instances', 0)) + 1
        
        # Update company tracking
        companies_list = author_data.get('Companies_List', '').split(';') if author_data.get('Companies_List') else []
        if company not in companies_list:
            companies_list.append(company)
            author_data['Total_Companies_Covered'] = len(companies_list)
            author_data['Companies_List'] = ';'.join(companies_list)
        
        # Update accuracy tracking
        if was_correct is True:
            author_data['Successful_Contrarian_Calls'] = int(author_data.get('Successful_Contrarian_Calls', 0)) + 1
        elif was_correct is False:
            author_data['Failed_Contrarian_Calls'] = int(author_data.get('Failed_Contrarian_Calls', 0)) + 1
        
        # Calculate success rate
        total_calls_with_results = int(author_data.get('Successful_Contrarian_Calls', 0)) + int(author_data.get('Failed_Contrarian_Calls', 0))
        if total_calls_with_results > 0:
            success_rate = (int(author_data.get('Successful_Contrarian_Calls', 0)) / total_calls_with_results) * 100
            author_data['Contrarian_Success_Rate'] = round(success_rate, 1)
        
        # Update scores
        current_total_score = float(author_data.get('Overall_Contrarian_Score', 0))
        author_data['Overall_Contrarian_Score'] = round(current_total_score + contrarian_score, 2)
        author_data['Average_Contrarian_Score_Per_Call'] = round(
            author_data['Overall_Contrarian_Score'] / author_data['Total_Contrarian_Instances'], 2
        )
        
        # Update latest information
        author_data['Last_Seen_Date'] = earnings_date
        author_data['Latest_Company'] = company
        author_data['Latest_Symbol'] = symbol
        author_data['Latest_Earnings_Date'] = earnings_date
        author_data['Latest_Contrarian_Type'] = contrarian_type
        author_data['Latest_Was_Correct'] = was_correct if was_correct is not None else 'Unknown'
        
        # Check for repeat contrarian behavior
        if int(author_data.get('Total_Contrarian_Instances', 0)) > 1:
            author_data['Repeat_Contrarian_Count'] = int(author_data.get('Total_Contrarian_Instances', 0)) - 1
        
        # Calculate consistency score (higher = more consistent contrarian)
        consistency = (author_data['Total_Contrarian_Instances'] / author_data['Total_Earnings_Calls']) * 100
        author_data['Consistency_Score'] = round(consistency, 1)
        
        # Determine risk level
        author_data['Risk_Level'] = self._calculate_risk_level(author_data)
        
        author_data['Last_Updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _create_new_author_record(self, author_name: str, author_id: str, company: str, 
                                symbol: str, earnings_date: str, contrarian_type: str, 
                                was_correct: Optional[bool], contrarian_score: float) -> Dict:
        """Create a new author record"""
        return {
            'Author_ID': author_id,
            'Author_Name': author_name,
            'First_Seen_Date': earnings_date,
            'Last_Seen_Date': earnings_date,
            'Total_Earnings_Calls': 1,
            'Total_Companies_Covered': 1,
            'Total_Contrarian_Instances': 1,
            'Successful_Contrarian_Calls': 1 if was_correct is True else 0,
            'Failed_Contrarian_Calls': 1 if was_correct is False else 0,
            'Contrarian_Success_Rate': 100.0 if was_correct is True else (0.0 if was_correct is False else None),
            'Overall_Contrarian_Score': contrarian_score,
            'Average_Contrarian_Score_Per_Call': contrarian_score,
            'Companies_List': company,
            'Latest_Company': company,
            'Latest_Symbol': symbol,
            'Latest_Earnings_Date': earnings_date,
            'Latest_Contrarian_Type': contrarian_type,
            'Latest_Was_Correct': was_correct if was_correct is not None else 'Unknown',
            'Repeat_Contrarian_Count': 0,
            'Consistency_Score': 100.0,  # First call is 100% consistent
            'Risk_Level': 'New',
            'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _calculate_risk_level(self, author_data: Dict) -> str:
        """Calculate risk level based on author's track record"""
        success_rate = author_data.get('Contrarian_Success_Rate')
        total_calls = int(author_data.get('Total_Contrarian_Instances', 0))
        consistency = author_data.get('Consistency_Score', 0)
        
        if success_rate is None or total_calls < 2:
            return 'Unknown'
        
        if success_rate >= 70 and total_calls >= 3:
            return 'Low_Risk'
        elif success_rate >= 50 and consistency >= 50:
            return 'Medium_Risk'
        elif success_rate < 30 or consistency < 20:
            return 'High_Risk'
        else:
            return 'Medium_Risk'
    
    def _save_author_history(self, author_id: str, author_name: str, company: str, 
                           symbol: str, earnings_date: str, contrarian_data: Dict, 
                           was_correct: Optional[bool]):
        """Save individual author's contrarian history"""
        history_file = os.path.join(self.author_history_dir, f"{author_id}_history.csv")
        
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(history_file)
        
        headers = [
            'Date_Added',
            'Author_Name',
            'Company',
            'Symbol',
            'Earnings_Date',
            'Sentiment',
            'Earnings_Prediction',
            'Contrarian_Type',
            'Contrarian_Score',
            'Was_Minority_Sentiment',
            'Was_Minority_Prediction',
            'Was_Correct',
            'Reasoning',
            'Key_Concerns'
        ]
        
        with open(history_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            
            if not file_exists:
                writer.writeheader()
            
            # Prepare key concerns
            key_concerns = contrarian_data.get('key_concerns', [])
            if isinstance(key_concerns, list):
                key_concerns_str = '; '.join(key_concerns)
            else:
                key_concerns_str = str(key_concerns) if key_concerns else ''
            
            row = {
                'Date_Added': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Author_Name': author_name,
                'Company': company,
                'Symbol': symbol,
                'Earnings_Date': earnings_date,
                'Sentiment': contrarian_data.get('sentiment', 'N/A'),
                'Earnings_Prediction': contrarian_data.get('earnings_prediction', 'N/A'),
                'Contrarian_Type': self._determine_contrarian_type(contrarian_data),
                'Contrarian_Score': contrarian_data.get('contrarian_score', 0),
                'Was_Minority_Sentiment': contrarian_data.get('was_minority_sentiment', False),
                'Was_Minority_Prediction': contrarian_data.get('was_minority_prediction', False),
                'Was_Correct': was_correct if was_correct is not None else 'Unknown',
                'Reasoning': contrarian_data.get('reasoning', ''),
                'Key_Concerns': key_concerns_str
            }
            
            writer.writerow(row)
    
    def _save_master_database(self, data: Dict[str, Dict]):
        """Save the updated master database"""
        headers = [
            'Author_ID', 'Author_Name', 'First_Seen_Date', 'Last_Seen_Date',
            'Total_Earnings_Calls', 'Total_Companies_Covered', 'Total_Contrarian_Instances',
            'Successful_Contrarian_Calls', 'Failed_Contrarian_Calls', 'Contrarian_Success_Rate',
            'Overall_Contrarian_Score', 'Average_Contrarian_Score_Per_Call', 'Companies_List',
            'Latest_Company', 'Latest_Symbol', 'Latest_Earnings_Date', 'Latest_Contrarian_Type',
            'Latest_Was_Correct', 'Repeat_Contrarian_Count', 'Consistency_Score', 'Risk_Level',
            'Last_Updated'
        ]
        
        with open(self.master_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for author_data in data.values():
                writer.writerow(author_data)
        
        print(f"Master database updated: {self.master_csv_path}")
    
    def _generate_update_summary(self, contrarians: List[Dict], company: str, 
                               symbol: str, earnings_date: str):
        """Generate a summary of the database update"""
        print(f"\n=== Master Database Update Summary ===")
        print(f"Company: {company} ({symbol})")
        print(f"Earnings Date: {earnings_date}")
        print(f"Contrarians Added/Updated: {len(contrarians)}")
        
        for i, contrarian in enumerate(contrarians, 1):
            author = contrarian.get('author', 'Unknown')
            score = contrarian.get('contrarian_score', 0)
            print(f"  {i}. {author} (Score: {score})")
        
        print(f"Database Location: {self.master_csv_path}")
        print(f"Author Histories: {self.author_history_dir}")
    
    def get_author_history(self, author_name: str) -> Optional[pd.DataFrame]:
        """Get the complete history for a specific author"""
        author_id = self._generate_author_id(author_name)
        history_file = os.path.join(self.author_history_dir, f"{author_id}_history.csv")
        
        if os.path.exists(history_file):
            return pd.read_csv(history_file)
        else:
            return None
    
    def get_top_contrarians(self, limit: int = 10, sort_by: str = 'Contrarian_Success_Rate') -> pd.DataFrame:
        """Get top contrarians from the master database"""
        if os.path.exists(self.master_csv_path):
            df = pd.read_csv(self.master_csv_path)
            return df.nlargest(limit, sort_by)
        else:
            return pd.DataFrame()
    
    def get_repeat_contrarians(self, min_instances: int = 2) -> pd.DataFrame:
        """Get authors who have been contrarians multiple times"""
        if os.path.exists(self.master_csv_path):
            df = pd.read_csv(self.master_csv_path)
            return df[df['Total_Contrarian_Instances'] >= min_instances]
        else:
            return pd.DataFrame()

def main():
    """Example usage of the Master Contrarian Database"""
    db = MasterContrarianDatabase()
    
    print("Master Contrarian Database initialized.")
    print(f"Database location: {db.master_csv_path}")
    print(f"Author histories: {db.author_history_dir}")
    
    # Example: Load existing contrarian reports and update database
    # Get the project root directory (two levels up from this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    reports_dir = os.path.join(project_root, "outputs")
    
    if os.path.exists(reports_dir):
        json_files = [f for f in os.listdir(reports_dir) if f.endswith('.json') and 'contrarian' in f]
        
        for json_file in json_files:
            json_path = os.path.join(reports_dir, json_file)
            try:
                with open(json_path, 'r') as f:
                    report_data = json.load(f)
                
                contrarians = report_data.get('contrarian_analysts', [])
                if contrarians:
                    print(f"\nProcessing: {json_file}")
                    db.add_contrarian_analysis(report_data, contrarians)
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
    
    # Show some statistics
    print("\n=== Database Statistics ===")
    top_contrarians = db.get_top_contrarians(5)
    if not top_contrarians.empty:
        print("\nTop 5 Contrarians by Success Rate:")
        for _, row in top_contrarians.iterrows():
            print(f"  {row['Author_Name']}: {row['Contrarian_Success_Rate']}% success, {row['Total_Contrarian_Instances']} instances")
    
    repeat_contrarians = db.get_repeat_contrarians(2)
    if not repeat_contrarians.empty:
        print(f"\nRepeat Contrarians ({len(repeat_contrarians)} authors with 2+ instances):")
        for _, row in repeat_contrarians.iterrows():
            print(f"  {row['Author_Name']}: {row['Total_Contrarian_Instances']} instances across {row['Total_Companies_Covered']} companies")

if __name__ == "__main__":
    main()