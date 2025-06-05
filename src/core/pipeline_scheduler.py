#!/usr/bin/env python3
"""
Pipeline Scheduler - Automated execution of sentiment analysis pipeline

This script provides scheduling capabilities for the automated pipeline:
- Run at specific times daily
- Run at regular intervals
- Monitor and restart failed runs
- Send notifications on completion/failure

Usage:
    python pipeline_scheduler.py [--config config.yaml] [--daemon] [--once]
"""

import os
import sys
import time
import yaml
import logging
import argparse
import subprocess
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import signal
import threading

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

class PipelineScheduler:
    """Scheduler for automated pipeline execution"""
    
    def __init__(self, config_path: str = 'pipeline_config.yaml'):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.setup_logging()
        self.running = False
        self.last_run_time = None
        self.last_run_success = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self) -> Dict:
        """Load pipeline configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging for scheduler"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        
        # Create logs directory if it doesn't exist
        log_path = project_root / 'logs'
        log_path.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path / 'scheduler.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('PipelineScheduler')
        self.logger.info("Scheduler logger initialized")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def run_pipeline(self, force_refresh: bool = False) -> bool:
        """Execute the pipeline"""
        self.logger.info("Starting scheduled pipeline execution")
        start_time = datetime.now()
        
        try:
            # Build command
            cmd = [sys.executable, str(project_root / 'automated_pipeline.py')]
            cmd.extend(['--config', str(self.config_path)])
            
            if force_refresh:
                cmd.append('--force-refresh')
            
            # Execute pipeline
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=7200  # 2 hour timeout
            )
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            # Update run status
            self.last_run_time = end_time
            self.last_run_success = (result.returncode == 0)
            
            if result.returncode == 0:
                self.logger.info(f"Pipeline completed successfully in {duration}")
                self.send_notification("SUCCESS", f"Pipeline completed in {duration}")
                return True
            else:
                self.logger.error(f"Pipeline failed after {duration}")
                self.logger.error(f"Error output: {result.stderr}")
                self.send_notification("FAILURE", f"Pipeline failed: {result.stderr[:500]}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Pipeline execution timed out")
            self.send_notification("TIMEOUT", "Pipeline execution timed out after 2 hours")
            return False
        except Exception as e:
            self.logger.error(f"Error running pipeline: {str(e)}")
            self.send_notification("ERROR", f"Scheduler error: {str(e)}")
            return False
    
    def send_notification(self, status: str, message: str):
        """Send notification about pipeline status"""
        notification_config = self.config.get('notifications', {})
        
        if not notification_config.get('enabled', False):
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"[{timestamp}] Pipeline {status}: {message}"
        
        # Email notification
        if notification_config.get('email', {}).get('enabled', False):
            self.send_email_notification(status, full_message)
        
        # Slack notification
        if notification_config.get('slack', {}).get('enabled', False):
            self.send_slack_notification(status, full_message)
    
    def send_email_notification(self, status: str, message: str):
        """Send email notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            email_config = self.config['notifications']['email']
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config.get('from_address', 'pipeline@localhost')
            msg['Subject'] = f"Pipeline {status} - Sentiment Analysis"
            
            # Add recipients
            recipients = email_config.get('recipients', [])
            if not recipients:
                return
            
            msg['To'] = ', '.join(recipients)
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config.get('smtp_port', 587))
            if email_config.get('use_tls', True):
                server.starttls()
            
            if 'username' in email_config and 'password' in email_config:
                server.login(email_config['username'], email_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Email notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
    
    def send_slack_notification(self, status: str, message: str):
        """Send Slack notification"""
        try:
            import requests
            
            slack_config = self.config['notifications']['slack']
            webhook_url = slack_config.get('webhook_url')
            
            if not webhook_url:
                return
            
            # Determine color based on status
            color_map = {
                'SUCCESS': 'good',
                'FAILURE': 'danger',
                'TIMEOUT': 'warning',
                'ERROR': 'danger'
            }
            
            payload = {
                'attachments': [{
                    'color': color_map.get(status, 'warning'),
                    'title': f'Pipeline {status}',
                    'text': message,
                    'ts': int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info("Slack notification sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {str(e)}")
    
    def setup_schedule(self):
        """Setup the execution schedule"""
        schedule_config = self.config.get('scheduling', {})
        
        if not schedule_config.get('enabled', False):
            self.logger.info("Scheduling is disabled")
            return
        
        # Daily run at specific time
        daily_time = schedule_config.get('daily_run_time')
        if daily_time:
            schedule.every().day.at(daily_time).do(self.run_pipeline)
            self.logger.info(f"Scheduled daily run at {daily_time}")
        
        # Interval-based runs
        interval_hours = schedule_config.get('interval_hours')
        if interval_hours:
            schedule.every(interval_hours).hours.do(self.run_pipeline)
            self.logger.info(f"Scheduled interval run every {interval_hours} hours")
        
        if not daily_time and not interval_hours:
            self.logger.warning("No schedule configured, running once")
            self.run_pipeline()
    
    def get_status(self) -> Dict:
        """Get current scheduler status"""
        next_run = None
        if schedule.jobs:
            next_run = schedule.next_run()
        
        return {
            'running': self.running,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'last_run_success': self.last_run_success,
            'next_run_time': next_run.isoformat() if next_run else None,
            'scheduled_jobs': len(schedule.jobs)
        }
    
    def run_daemon(self):
        """Run scheduler as daemon"""
        self.logger.info("Starting scheduler daemon")
        self.running = True
        
        # Setup schedule
        self.setup_schedule()
        
        # Main loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                self.logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
        
        self.logger.info("Scheduler daemon stopped")
    
    def run_once(self, force_refresh: bool = False):
        """Run pipeline once and exit"""
        self.logger.info("Running pipeline once")
        success = self.run_pipeline(force_refresh=force_refresh)
        
        if success:
            self.logger.info("Single run completed successfully")
        else:
            self.logger.error("Single run failed")
        
        return success

def create_systemd_service():
    """Create a systemd service file for the scheduler"""
    service_content = f"""[Unit]
Description=Sentiment Analysis Pipeline Scheduler
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={project_root}
ExecStart={sys.executable} {project_root}/pipeline_scheduler.py --daemon
Restart=always
RestartSec=30
Environment=PATH={os.environ.get('PATH', '')}
Environment=PYTHONPATH={project_root}

[Install]
WantedBy=multi-user.target
"""
    
    service_file = project_root / 'sentiment-pipeline.service'
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"Systemd service file created: {service_file}")
    print("To install:")
    print(f"  sudo cp {service_file} /etc/systemd/system/")
    print("  sudo systemctl daemon-reload")
    print("  sudo systemctl enable sentiment-pipeline")
    print("  sudo systemctl start sentiment-pipeline")

def create_cron_job():
    """Create a cron job for the scheduler"""
    cron_command = f"{sys.executable} {project_root}/pipeline_scheduler.py --once"
    
    print("To setup cron job, add this line to your crontab (crontab -e):")
    print(f"# Run sentiment analysis pipeline every 6 hours")
    print(f"0 */6 * * * {cron_command}")
    print("")
    print("Or for daily runs at 9 AM:")
    print(f"0 9 * * * {cron_command}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Pipeline Scheduler')
    parser.add_argument('--config', default='pipeline_config.yaml', help='Configuration file path')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--force-refresh', action='store_true', help='Force refresh all data')
    parser.add_argument('--status', action='store_true', help='Show scheduler status')
    parser.add_argument('--create-service', action='store_true', help='Create systemd service file')
    parser.add_argument('--create-cron', action='store_true', help='Show cron job setup instructions')
    
    args = parser.parse_args()
    
    # Handle utility commands
    if args.create_service:
        create_systemd_service()
        return
    
    if args.create_cron:
        create_cron_job()
        return
    
    # Initialize scheduler
    scheduler = PipelineScheduler(args.config)
    
    if args.status:
        status = scheduler.get_status()
        print("Scheduler Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        return
    
    # Run scheduler
    if args.once:
        success = scheduler.run_once(force_refresh=args.force_refresh)
        sys.exit(0 if success else 1)
    elif args.daemon:
        scheduler.run_daemon()
    else:
        print("Please specify --daemon, --once, or --status")
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()