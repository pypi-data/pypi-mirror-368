"""
HLA-Compass Python SDK
SDK for developing modules on the HLA-Compass platform
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(    name="hla-compass",  # Shorter name for easier installation
    version="1.0.8",
    author="Alithea Bio",
    author_email="dev@alithea.bio",
    description="Python SDK for HLA-Compass bioinformatics platform - Build powerful modules for immuno-peptidomics analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlitheaBio/HLA-Compass-platform",
    project_urls={
        "Bug Tracker": "https://github.com/AlitheaBio/HLA-Compass-platform/issues",
        "Documentation": "https://docs.hla-compass.com",
        "Source Code": "https://github.com/AlitheaBio/HLA-Compass-platform/tree/main/sdk/python",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "boto3>=1.26.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
        "python-dotenv>=0.19.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "PyYAML>=6.0",
        "setuptools>=45.0.0",  # Required for pkg_resources compatibility
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.6.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "ml": [
            "scikit-learn>=1.0.0",
            "torch>=1.10.0",
            "transformers>=4.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hla-compass=hla_compass.cli:main",
        ],
    },
    package_data={
        "hla_compass": ["templates/**/*", "data/*"],
    },
    include_package_data=True,
)