#!/usr/bin/env python3
"""
CLI commands for VTON Evaluation Suite.

Provides three main commands:
- vton-eval: Run evaluation on VTON model submissions
- vton-validate: Validate submission format and data
- vton-setup: Setup environment and download models
"""

import argparse
import sys
import os
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from vton_eval.core.config import VTONConfig
from vton_eval.pipeline import VTONEvaluationPipeline
from vton_eval.core.data_models import EvaluationTask
import numpy as np
import cv2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for vton-eval command."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'evaluate':
            run_evaluation(args)
        elif args.command == 'validate':
            validate_submission(args)
        elif args.command == 'setup':
            setup_environment(args)
        elif args.command == 'version':
            print_version()
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI commands."""
    parser = argparse.ArgumentParser(
        description="VTON Evaluation Suite - Comprehensive evaluation framework for Virtual Try-On models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate a submission
  vton-eval evaluate --submission-dir ./submission --output ./results
  
  # Validate submission format
  vton-eval validate --submission-dir ./submission
  
  # Setup environment and download models
  vton-eval setup --download-models

For more information, visit: https://github.com/your-org/vton-eval
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Evaluate command
    eval_parser = subparsers.add_parser(
        'evaluate', 
        help='Run evaluation on VTON model submission',
        description='Evaluate a VTON model submission using all configured evaluators'
    )
    eval_parser.add_argument(
        '--submission-dir', '-s',
        required=True, 
        help='Path to submission directory containing generated images'
    )
    eval_parser.add_argument(
        '--output', '-o',
        required=True, 
        help='Path to output directory for results'
    )
    eval_parser.add_argument(
        '--config', '-c',
        default='configs/default_config.yaml',
        help='Path to configuration file (default: configs/default_config.yaml)'
    )
    eval_parser.add_argument(
        '--resume', '-r',
        help='Resume from checkpoint file'
    )
    eval_parser.add_argument(
        '--no-visualizations',
        action='store_true',
        help='Disable visualization generation'
    )
    eval_parser.add_argument(
        '--batch-size',
        type=int,
        help='Override batch size from config'
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        'validate', 
        help='Validate submission format and data',
        description='Check if submission follows required format and all files are present'
    )
    validate_parser.add_argument(
        '--submission-dir', '-s',
        required=True, 
        help='Path to submission directory to validate'
    )
    validate_parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation (check image dimensions, formats, etc.)'
    )
    validate_parser.add_argument(
        '--output', '-o',
        help='Save validation report to file'
    )

    # Setup command
    setup_parser = subparsers.add_parser(
        'setup', 
        help='Setup environment and download models',
        description='Setup VTON evaluation environment and download required models'
    )
    setup_parser.add_argument(
        '--download-models',
        action='store_true', 
        help='Download all required models (SAM, CLIP, etc.)'
    )
    setup_parser.add_argument(
        '--config', '-c',
        default='configs/default_config.yaml',
        help='Path to configuration file'
    )
    setup_parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check environment without making changes'
    )
    setup_parser.add_argument(
        '--models-dir',
        default='./models',
        help='Directory to store downloaded models'
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        'version',
        help='Show version information'
    )

    return parser


def run_evaluation(args):
    """Run evaluation on submission."""
    logger.info("=" * 60)
    logger.info("VTON Evaluation Suite")
    logger.info("=" * 60)
    
    # Validate paths
    submission_dir = Path(args.submission_dir)
    if not submission_dir.exists():
        raise FileNotFoundError(f"Submission directory not found: {submission_dir}")
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load configuration
    logger.info(f"Loading configuration from: {args.config}")
    config = VTONConfig(args.config)
    
    # Validate configuration
    if not config.validate():
        raise ValueError("Invalid configuration")
    
    # Override settings from command line
    if args.no_visualizations:
        config.config['reporting']['include_visualizations'] = False
    
    if args.batch_size:
        config.config['evaluation']['batch_size'] = args.batch_size
    
    # Check for API key
    if not config.config['vlm'].get('api_key'):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            config.config['vlm']['api_key'] = api_key
            logger.info("Using GEMINI_API_KEY from environment")
        else:
            logger.warning("No API key found for VLM backend. Some features may be limited.")
    
    # Create pipeline
    logger.info("Initializing evaluation pipeline...")
    pipeline = VTONEvaluationPipeline(config)
    
    # Resume from checkpoint if specified
    if args.resume:
        logger.info(f"Resuming from checkpoint: {args.resume}")
        resume_status = pipeline.resume_evaluation(args.resume)
        if resume_status['status'] == 'error':
            raise RuntimeError(f"Failed to resume: {resume_status['error']}")
    
    # Run evaluation
    logger.info(f"Starting evaluation of: {submission_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    try:
        results = pipeline.evaluate_submission(str(submission_dir), str(output_dir))
        
        # Print summary
        if 'summary' in results:
            logger.info("\n" + "=" * 60)
            logger.info("EVALUATION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total samples evaluated: {results['num_samples']}")
            logger.info(f"Mean overall score: {results['summary']['mean_scores']['overall']:.3f}")
            logger.info(f"Production ready: {results['summary']['production_ready_percentage']:.1f}%")
            
            # Component scores
            logger.info("\nComponent Scores:")
            for component in ['garment', 'identity', 'body', 'fit']:
                if component in results['summary']['mean_scores']:
                    score = results['summary']['mean_scores'][component]
                    logger.info(f"  {component.capitalize()}: {score:.3f}")
            
            # Quality distribution
            if 'detailed_report' in results and 'score_distribution' in results['detailed_report']:
                logger.info("\nQuality Distribution:")
                for tier, count in results['detailed_report']['score_distribution'].items():
                    logger.info(f"  {tier.capitalize()}: {count} samples")
        
        logger.info(f"\nResults saved to: {output_dir}")
        logger.info("Evaluation completed successfully!")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise


def validate_submission(args):
    """Validate submission format and data."""
    logger.info("Validating submission format...")
    
    submission_dir = Path(args.submission_dir)
    if not submission_dir.exists():
        raise FileNotFoundError(f"Submission directory not found: {submission_dir}")
    
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'statistics': {}
    }
    
    try:
        # Check for metadata file
        metadata_path = submission_dir / 'metadata.json'
        if not metadata_path.exists():
            validation_results['errors'].append("Missing metadata.json file")
            validation_results['valid'] = False
        else:
            # Validate metadata
            with open(metadata_path, 'r') as f:
                try:
                    metadata = json.load(f)
                    validation_results['statistics']['num_samples'] = len(metadata)
                    
                    # Check each entry
                    for idx, entry in enumerate(metadata):
                        # Required fields
                        required_fields = ['id', 'human_image', 'garment_image']
                        for field in required_fields:
                            if field not in entry:
                                validation_results['errors'].append(
                                    f"Entry {idx}: Missing required field '{field}'"
                                )
                                validation_results['valid'] = False
                        
                        # Check if generated image exists
                        if 'id' in entry:
                            generated_path = submission_dir / f"{entry['id']}_generated.jpg"
                            alt_path = submission_dir / f"{entry['id']}.jpg"
                            
                            if not generated_path.exists() and not alt_path.exists():
                                validation_results['errors'].append(
                                    f"Missing generated image for sample: {entry['id']}"
                                )
                                validation_results['valid'] = False
                            
                            # Strict validation
                            if args.strict and (generated_path.exists() or alt_path.exists()):
                                img_path = generated_path if generated_path.exists() else alt_path
                                img = cv2.imread(str(img_path))
                                
                                if img is None:
                                    validation_results['errors'].append(
                                        f"Failed to load image: {img_path}"
                                    )
                                else:
                                    h, w = img.shape[:2]
                                    if h < 256 or w < 256:
                                        validation_results['warnings'].append(
                                            f"Low resolution image ({w}x{h}): {img_path}"
                                        )
                
                except json.JSONDecodeError as e:
                    validation_results['errors'].append(f"Invalid JSON in metadata.json: {e}")
                    validation_results['valid'] = False
        
        # Count generated images
        generated_images = list(submission_dir.glob("*_generated.jpg")) + \
                          list(submission_dir.glob("*.jpg"))
        validation_results['statistics']['num_images'] = len(generated_images)
        
        # Check for common issues
        if validation_results['statistics'].get('num_samples', 0) == 0:
            validation_results['errors'].append("No samples found in metadata")
            validation_results['valid'] = False
        
        # Print results
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION RESULTS")
        logger.info("=" * 60)
        logger.info(f"Valid: {'YES' if validation_results['valid'] else 'NO'}")
        logger.info(f"Samples in metadata: {validation_results['statistics'].get('num_samples', 0)}")
        logger.info(f"Generated images found: {validation_results['statistics'].get('num_images', 0)}")
        
        if validation_results['errors']:
            logger.error(f"\nErrors ({len(validation_results['errors'])}):")
            for error in validation_results['errors'][:10]:  # Show first 10
                logger.error(f"  - {error}")
            if len(validation_results['errors']) > 10:
                logger.error(f"  ... and {len(validation_results['errors']) - 10} more errors")
        
        if validation_results['warnings']:
            logger.warning(f"\nWarnings ({len(validation_results['warnings'])}):")
            for warning in validation_results['warnings'][:5]:  # Show first 5
                logger.warning(f"  - {warning}")
            if len(validation_results['warnings']) > 5:
                logger.warning(f"  ... and {len(validation_results['warnings']) - 5} more warnings")
        
        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(validation_results, f, indent=2)
            logger.info(f"\nValidation report saved to: {args.output}")
        
        if validation_results['valid']:
            logger.info("\nSubmission is valid and ready for evaluation!")
        else:
            logger.error("\nSubmission validation failed. Please fix the errors and try again.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise


def setup_environment(args):
    """Setup VTON evaluation environment."""
    logger.info("Setting up VTON evaluation environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    logger.info(f"Python version: {sys.version}")
    
    # Check required packages
    required_packages = [
        'numpy', 'torch', 'torchvision', 'opencv-python', 'pillow',
        'scikit-image', 'tensorflow', 'google-genai', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"✗ {package} is not installed")
    
    if missing_packages and not args.check_only:
        logger.info(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
    
    # Download models if requested
    if args.download_models and not args.check_only:
        logger.info("\nDownloading required models...")
        
        # Load config to get model specifications
        config = VTONConfig(args.config) if args.config else None
        
        # Create models directory
        models_dir = Path(args.models_dir)
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Download SAM model
        logger.info("\nDownloading SAM model...")
        sam_dir = models_dir / 'sam2'
        sam_dir.mkdir(exist_ok=True)
        
        # Run download script if it exists
        download_script = Path('scripts/download_models.py')
        if download_script.exists():
            subprocess.run([sys.executable, str(download_script), '--models-dir', str(models_dir)])
        else:
            logger.warning("Download script not found. Please download models manually.")
    
    # Check environment variables
    logger.info("\nChecking environment variables...")
    if os.getenv('GEMINI_API_KEY'):
        logger.info("✓ GEMINI_API_KEY is set")
    else:
        logger.warning("✗ GEMINI_API_KEY is not set (required for VLM features)")
        logger.info("  Set it with: export GEMINI_API_KEY='your-api-key'")
    
    # Verify installation
    logger.info("\nVerifying installation...")
    try:
        from vton_eval.pipeline import VTONEvaluationPipeline
        from vton_eval.core.config import VTONConfig
        logger.info("✓ VTON evaluation package is properly installed")
    except ImportError as e:
        logger.error(f"✗ Failed to import VTON evaluation package: {e}")
        logger.info("  Make sure you're in the correct directory or install the package")
    
    if args.check_only:
        logger.info("\nEnvironment check completed (no changes made)")
    else:
        logger.info("\nEnvironment setup completed!")
        logger.info("You can now run: vton-eval evaluate --help")


def print_version():
    """Print version information."""
    try:
        import importlib.metadata
        version = importlib.metadata.version('vybe-vton-eval')
    except:
        version = "0.1.0"  # Fallback version
    
    print(f"VTON Evaluation Suite v{version}")
    print("Copyright (c) 2024 Arnab Ghosh")
    print("Licensed under MIT License")


def validate_main():
    """Entry point for vton-validate command."""
    parser = argparse.ArgumentParser(
        description='Validate VTON submission format',
        prog='vton-validate'
    )
    parser.add_argument(
        'submission_dir',
        help='Path to submission directory to validate'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict validation'
    )
    parser.add_argument(
        '--output', '-o',
        help='Save validation report to file'
    )
    
    args = parser.parse_args()
    
    # Convert to format expected by validate_submission
    class Args:
        submission_dir = args.submission_dir
        strict = args.strict
        output = args.output
    
    try:
        validate_submission(Args())
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


def setup_main():
    """Entry point for vton-setup command."""
    parser = argparse.ArgumentParser(
        description='Setup VTON evaluation environment',
        prog='vton-setup'
    )
    parser.add_argument(
        '--download-models',
        action='store_true',
        help='Download required models'
    )
    parser.add_argument(
        '--config', '-c',
        default='configs/default_config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check environment without making changes'
    )
    parser.add_argument(
        '--models-dir',
        default='./models',
        help='Directory to store downloaded models'
    )
    
    args = parser.parse_args()
    
    try:
        setup_environment(args)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
