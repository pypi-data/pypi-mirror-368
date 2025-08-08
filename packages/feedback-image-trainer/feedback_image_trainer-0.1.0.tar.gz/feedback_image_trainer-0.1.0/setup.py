import os
from setuptools import setup, find_packages




with open("README.md", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="feedback_image_trainer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Fine-tune Stable Diffusion with feedback-driven Optuna hyperparameter search",
    long_description=open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "diffusers>=0.20.0",
        "transformers>=4.30.0",
        "accelerate>=0.20.0",
        "optuna>=2.0.0",
        "torchvision>=0.15.0",
    ],
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)