from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A comprehensive library for epitope prediction and immunogenicity analysis"

setup(
    name="immunoforge",
    version="0.1.1",
    author="Nicolas Lynn",
    author_email="nicolas.lynn@example.com",
    description="A comprehensive library for epitope prediction and immunogenicity analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nicolaslynn/immunoforge",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "mhcflurry>=2.0.0",
        "tensorflow>=2.6.0",
        "scikit-learn>=0.24.0",
        "biopython>=1.79",
        "tqdm>=4.62.0",
        "pyyaml>=5.4.0",
        "xlsxwriter>=3.0.0",
        "joblib>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
        "deepimmuno": [
            "torch>=1.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "immunoforge=immunoforge.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "immunoforge": ["data/*.json", "data/*.yaml"],
    },
)