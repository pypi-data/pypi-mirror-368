"""
Setup script for vishuml package.

This script allows the package to be installed via pip and uploaded to PyPI.
"""

from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vishuml",
    version="0.1.1",
    author="Vishu pratap",
    author_email="vishurizz0@gmail.com",
    description="A machine learning library implementing algorithms from scratch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vishuRizz/vishuml-pip-library",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "jupyter>=1.0",
            "matplotlib>=3.0",
            "pandas>=1.0",
        ],
    },
    include_package_data=True,
    package_data={
        "vishuml": [
            "datasets/*.csv",
        ],
    },
    keywords="machine learning, algorithms, classification, regression, clustering, data science",
    project_urls={
        "Bug Reports": "https://github.com/vishuRizz/vishuml-pip-library/issues",
        "Source": "https://github.com/vishuRizz/vishuml-pip-library",
        "Documentation": "https://github.com/vishuRizz/vishuml-pip-library#readme",
    },
)
