# VTON Evaluation Suite

A comprehensive evaluation suite for Virtual Try-On (VTON) models.

## Installation

```bash
# Install from PyPI (after publication)
pip install vton-eval

# Development installation
git clone https://github.com/your-org/vton-eval.git
cd vton-eval
pip install -e .[dev]

# Setup models and environment
vton-setup --download-models --gpu
```

## Basic Usage

```python
# Python API
from vton_eval import VTONConfig, VTONEvaluationPipeline

config = VTONConfig.from_file('evaluation_config.yaml')
pipeline = VTONEvaluationPipeline(config)

# Evaluate a submission directory
results = pipeline.evaluate_submission(
    submission_dir='submissions/my_model/',
    output_path='results/my_model_results.json'
)

print(f"VTON Score: {results['overall_score']:.3f}")
print(f"Production Ready: {results['production_ready']}")
```

### Command Line Usage
```bash
# Basic evaluation
vton-eval evaluate --submission-dir submissions/model_a/ --output results.json

# Custom configuration
vton-eval evaluate --config custom_config.yaml --submission-dir submissions/model_b/ --output results_b.json

# Validate submission format
vton-eval validate --submission-dir submissions/model_c/

# Setup and model download
vton-eval setup --download-models --config-template advanced
```
