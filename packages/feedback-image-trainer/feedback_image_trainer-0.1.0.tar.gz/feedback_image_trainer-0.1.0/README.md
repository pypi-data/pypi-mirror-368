#### overview
```markdown
# Feedback Image Trainer

A Python package to fine-tune Stable Diffusion models using feedback-driven hyperparameter search with Optuna.

## Installation

```bash
pip install feedback_image_trainer
```

## Usage

```python
from feedback_image_trainer import run_study

run_study(
    feedback_file="image_feedback.json",
    model_path="runwayml/stable-diffusion-v1-5",
    output_dir="fine_tuned_model",
    trials=5
)
```

## Input Data Format

The `image_feedback.json` file should contain a list of dictionaries with the following structure:

```json
[
    {
        "image_path": "path/to/image.png",
        "prompt": "A description of the image",
        "feedback": 1
    },
    ...
]
```

## Requirements

- Python 3.8+
- torch>=2.0.0
- diffusers>=0.20.0
- transformers>=4.30.0
- accelerate>=0.20.0
- optuna>=2.0.0
- torchvision>=0.15.0

