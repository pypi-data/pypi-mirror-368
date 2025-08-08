"""Setup script for PodFeed SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="podfeed-sdk",
    version="0.3.0",
    author="PodFeed",
    author_email="support@podfeed.ai",
    description="A Python SDK for the PodFeed API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smh-labs/podfeed-sdk-samples",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
        ],
    },
    keywords="podfeed, audio, podcast, tts, text-to-speech, api, sdk",
    project_urls={
        "Bug Reports": "https://github.com/podfeed/podfeed-sdk-python/issues",
        "Source": "https://github.com/podfeed/podfeed-sdk-python",
        "Documentation": "https://docs.podfeed.ai",
    },
)
