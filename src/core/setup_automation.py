#!/usr/bin/env python3
"""
Setup Script for Automated Sentiment Analysis Pipeline

This script helps you set up and configure the automation system:
- Install dependencies
- Validate notebook paths
- Test configuration
- Create necessary directories
- Run initial setup checks

Usage:
    python setup_automation.py [--install-deps] [--test-notebooks] [--create-sample-config]
"""

import os
import sys
import subprocess
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

project_root = Path(__file__).parent

class AutomationSetup:
    """Setup and validation for the automation system"""
    
    def __init__(self):
        self.project_root = project_root
        self.config_file = self.project_root / 'pipeline_config.yaml'
        self.requirements_file = self.project_root / 'requirements.txt'
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str, status: str = None):
        """Print a setup step with optional status"""
        if status:
            print(f"  {step:<50} [{status}]")
        else:
            print(f"  {step}")
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.print_step(f"Python version {version.major}.{version.minor}.{version.micro}", "✓ OK")
            return True
        else:
            self.print_step(f"Python version {version.major}.{version.minor}.{version.micro}", "✗ FAIL")
            print("    Error: Python 3.8+ required")
            return False
    
    def install_dependencies(self) -> bool:
        """Install required Python packages"""
        self.print_header("Installing Dependencies")
        
        if not self.requirements_file.exists():
            self.print_step("requirements.txt not found", "✗ FAIL")
            return False
        
        try:
            self.print_step("Installing packages from requirements.txt...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(self.requirements_file)],
                capture_output=True,
                text=True,
                check=True
            )
            self.print_step("Package installation", "✓ OK")
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_step("Package installation", "✗ FAIL")
            print(f"    Error: {e.stderr}")
            return False
    
    def create_directories(self) -> bool:
        """Create necessary directories"""
        self.print_header("Creating Directories")
        
        directories = [
            'logs',
            'reports',
            'backups'
        ]
        
        success = True
        for directory in directories:
            dir_path = self.project_root / directory
            try:
                dir_path.mkdir(exist_ok=True)
                self.print_step(f"Directory: {directory}/", "✓ OK")
            except Exception as e:
                self.print_step(f"Directory: {directory}/", "✗ FAIL")
                print(f"    Error: {str(e)}")
                success = False
        
        return success
    
    def validate_config(self) -> Tuple[bool, Dict]:
        """Validate pipeline configuration"""
        self.print_header("Validating Configuration")
        
        if not self.config_file.exists():
            self.print_step("Configuration file", "✗ MISSING")
            print(f"    Error: {self.config_file} not found")
            return False, {}
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            self.print_step("Configuration file syntax", "✓ OK")
            
            # Validate required sections
            required_sections = [
                'data_collection',
                'sentiment_analysis',
                'contrarian_analysis',
                'signal_generation',
                'companies'
            ]
            
            missing_sections = []
            for section in required_sections:
                if section in config:
                    self.print_step(f"Section: {section}", "✓ OK")
                else:
                    self.print_step(f"Section: {section}", "✗ MISSING")
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"    Error: Missing required sections: {missing_sections}")
                return False, config
            
            return True, config
            
        except yaml.YAMLError as e:
            self.print_step("Configuration file syntax", "✗ FAIL")
            print(f"    Error: Invalid YAML syntax: {str(e)}")
            return False, {}
        except Exception as e:
            self.print_step("Configuration file", "✗ FAIL")
            print(f"    Error: {str(e)}")
            return False, {}
    
    def validate_notebooks(self, config: Dict) -> bool:
        """Validate that all required notebooks exist"""
        self.print_header("Validating Notebook Paths")
        
        if 'companies' not in config or 'apple' not in config['companies']:
            self.print_step("Apple company configuration", "✗ MISSING")
            return False
        
        apple_config = config['companies']['apple']
        if 'notebooks' not in apple_config:
            self.print_step("Notebook configuration", "✗ MISSING")
            return False
        
        notebooks = apple_config['notebooks']
        success = True
        
        for step, notebook_path in notebooks.items():
            abs_path = self.project_root / notebook_path
            if abs_path.exists():
                self.print_step(f"Notebook: {step}", "✓ OK")
                self.print_step(f"  Path: {notebook_path}")
            else:
                self.print_step(f"Notebook: {step}", "✗ MISSING")
                self.print_step(f"  Path: {notebook_path}")
                success = False
        
        return success
    
    def test_notebook_execution(self, config: Dict) -> bool:
        """Test notebook execution (dry run)"""
        self.print_header("Testing Notebook Execution")
        
        try:
            # Test if jupyter is available
            result = subprocess.run(
                ['jupyter', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            self.print_step("Jupyter installation", "✓ OK")
            
            # Test nbconvert
            result = subprocess.run(
                ['jupyter', 'nbconvert', '--help'],
                capture_output=True,
                text=True,
                check=True
            )
            self.print_step("nbconvert availability", "✓ OK")
            
            return True
            
        except subprocess.CalledProcessError:
            self.print_step("Jupyter/nbconvert", "✗ FAIL")
            print("    Error: Jupyter or nbconvert not available")
            print("    Install with: pip install jupyter nbconvert")
            return False
        except FileNotFoundError:
            self.print_step("Jupyter installation", "✗ FAIL")
            print("    Error: Jupyter not found in PATH")
            return False
    
    def validate_data_files(self, config: Dict) -> bool:
        """Validate data file paths (optional - will be created)"""
        self.print_header("Checking Data Files")
        
        if 'companies' not in config or 'apple' not in config['companies']:
            return True
        
        apple_config = config['companies']['apple']
        if 'data_files' not in apple_config:
            return True
        
        data_files = apple_config['data_files']
        
        for data_type, file_path in data_files.items():
            abs_path = self.project_root / file_path
            if abs_path.exists():
                self.print_step(f"Data file: {data_type}", "✓ EXISTS")
                self.print_step(f"  Path: {file_path}")
            else:
                self.print_step(f"Data file: {data_type}", "? WILL BE CREATED")
                self.print_step(f"  Path: {file_path}")
        
        return True
    
    def test_pipeline_dry_run(self) -> bool:
        """Test the pipeline with dry run"""
        self.print_header("Testing Pipeline (Dry Run)")
        
        pipeline_script = self.project_root / 'automated_pipeline.py'
        if not pipeline_script.exists():
            self.print_step("Pipeline script", "✗ MISSING")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(pipeline_script), '--dry-run'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.print_step("Pipeline dry run", "✓ OK")
                return True
            else:
                self.print_step("Pipeline dry run", "✗ FAIL")
                print(f"    Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.print_step("Pipeline dry run", "✗ TIMEOUT")
            return False
        except Exception as e:
            self.print_step("Pipeline dry run", "✗ FAIL")
            print(f"    Error: {str(e)}")
            return False
    
    def create_sample_config(self) -> bool:
        """Create a sample configuration file"""
        self.print_header("Creating Sample Configuration")
        
        sample_config_path = self.project_root / 'pipeline_config_sample.yaml'
        
        if sample_config_path.exists():
            self.print_step("Sample config already exists", "? SKIP")
            return True
        
        try:
            # Copy existing config as sample
            if self.config_file.exists():
                import shutil
                shutil.copy2(self.config_file, sample_config_path)
                self.print_step("Sample configuration created", "✓ OK")
                self.print_step(f"  Path: {sample_config_path}")
            else:
                self.print_step("No existing config to copy", "? SKIP")
            
            return True
            
        except Exception as e:
            self.print_step("Sample configuration", "✗ FAIL")
            print(f"    Error: {str(e)}")
            return False
    
    def print_next_steps(self):
        """Print next steps for the user"""
        self.print_header("Next Steps")
        
        print("  1. Review and customize pipeline_config.yaml")
        print("  2. Test the pipeline:")
        print("     python automated_pipeline.py --dry-run")
        print("  3. Run the pipeline once:")
        print("     python automated_pipeline.py")
        print("  4. Set up scheduling:")
        print("     python pipeline_scheduler.py --daemon")
        print("  5. Monitor logs:")
        print("     tail -f logs/pipeline_v0.log")
        print("")
        print("  For detailed instructions, see: README_AUTOMATION.md")
        print("")
    
    def run_full_setup(self, install_deps: bool = False, test_notebooks: bool = False) -> bool:
        """Run the complete setup process"""
        print("Automated Sentiment Analysis Pipeline - Setup")
        print(f"Project Root: {self.project_root}")
        
        success = True
        
        # Check Python version
        self.print_header("System Requirements")
        if not self.check_python_version():
            success = False
        
        # Install dependencies if requested
        if install_deps:
            if not self.install_dependencies():
                success = False
        
        # Create directories
        if not self.create_directories():
            success = False
        
        # Validate configuration
        config_valid, config = self.validate_config()
        if not config_valid:
            success = False
        
        # Validate notebooks
        if config_valid:
            if not self.validate_notebooks(config):
                success = False
        
        # Test notebook execution if requested
        if test_notebooks and config_valid:
            if not self.test_notebook_execution(config):
                success = False
        
        # Validate data files
        if config_valid:
            self.validate_data_files(config)
        
        # Test pipeline dry run
        if config_valid:
            if not self.test_pipeline_dry_run():
                success = False
        
        # Print results
        self.print_header("Setup Results")
        if success:
            self.print_step("Overall setup status", "✓ SUCCESS")
            self.print_next_steps()
        else:
            self.print_step("Overall setup status", "✗ ISSUES FOUND")
            print("\n  Please fix the issues above before proceeding.")
            print("  Run setup again after making corrections.")
        
        return success

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Setup Automated Pipeline')
    parser.add_argument('--install-deps', action='store_true', help='Install Python dependencies')
    parser.add_argument('--test-notebooks', action='store_true', help='Test notebook execution capabilities')
    parser.add_argument('--create-sample-config', action='store_true', help='Create sample configuration file')
    parser.add_argument('--full-setup', action='store_true', help='Run complete setup process')
    
    args = parser.parse_args()
    
    setup = AutomationSetup()
    
    if args.create_sample_config:
        setup.create_sample_config()
        return
    
    if args.full_setup or not any([args.install_deps, args.test_notebooks, args.create_sample_config]):
        # Run full setup if no specific options or --full-setup specified
        success = setup.run_full_setup(
            install_deps=args.install_deps,
            test_notebooks=args.test_notebooks
        )
        sys.exit(0 if success else 1)
    else:
        # Run specific setup steps
        if args.install_deps:
            setup.install_dependencies()
        
        if args.test_notebooks:
            _, config = setup.validate_config()
            if config:
                setup.test_notebook_execution(config)

if __name__ == '__main__':
    main()