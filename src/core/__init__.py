# Contrarian Analysis Pipeline - Core Package

# Import core modules for easier access
try:
    from .automated_pipeline import AutomatedPipeline
    from .pipeline_scheduler import PipelineScheduler
    from .run_output_generator import RunOutputGenerator
    from .setup_automation import SetupAutomation
except ImportError as e:
    # Handle import errors gracefully during development
    print(f"Warning: Could not import some core modules: {e}")

__all__ = [
    'AutomatedPipeline',
    'PipelineScheduler',
    'RunOutputGenerator',
    'SetupAutomation'
]