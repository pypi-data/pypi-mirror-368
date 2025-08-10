"""Setup script for tap2talk."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text()
else:
    long_description = "Tap2Talk - Voice transcription desktop application"

setup(
    name="tap2talk",
    version="0.1.0",
    author="Tap2Talk",
    description="A minimal voice transcription desktop app that runs in the background",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "groq>=0.11.0",
        "sounddevice>=0.5.0",
        "numpy>=1.24.0",
        "PyYAML>=6.0",
        "pystray>=0.19.0",
        "Pillow>=10.0.0",
        "pyperclip>=1.8.0",
        "pynput>=1.7.0",
    ],
    extras_require={
        "mac": [
            "pyobjc-framework-Quartz>=10.0",
            "pyobjc-framework-ApplicationServices>=10.0",
        ],
        "win": [
            "pywin32>=305",
            "keyboard>=0.13.5",
        ],
        "audio": [
            "resampy>=0.4.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tap2talk=tap2talk.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
)