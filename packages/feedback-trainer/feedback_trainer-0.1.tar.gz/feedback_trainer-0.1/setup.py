# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="feedback_trainer",
    version="0.1",
    author="Your Name",
    author_email="you@example.com",
    description="Train QA model with feedback using Optuna and SimpleTransformers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "simpletransformers>=0.63.9",
        "optuna>=3.0.0"
    ],
    python_requires=">=3.8",
)
