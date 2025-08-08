#!/usr/bin/env python3
"""Setup script for Shaheen-Jarvis framework."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shaheen-jarvis",
    version="0.3.0",
    author="Engr. Hamza",
    description="A powerful, voice-enabled AI assistant framework with comprehensive speech recognition, natural language processing, and extensive API integrations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/shaheen-jarvis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pyttsx3>=2.90",
        "SpeechRecognition>=3.8.1",
        "wikipedia>=1.4.0",
        "psutil>=5.9.0",
        "gTTS>=2.2.4",
        "pyaudio>=0.2.11",
        "openai>=0.27.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "PyYAML>=6.0",
        "colorama>=0.4.4",
        "click>=8.0.0",
        "sounddevice>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
    },
    entry_points={
        "console_scripts": [
            "jarvis=jarvis.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
