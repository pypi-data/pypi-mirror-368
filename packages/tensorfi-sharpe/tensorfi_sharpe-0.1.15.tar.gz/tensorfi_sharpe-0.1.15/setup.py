from setuptools import setup, find_packages
import os

# test


def read_requirements(filename):
    """Read requirements from a requirements file, filtering out comments and empty lines."""
    if not os.path.exists(filename):
        return []

    with open(filename, "r") as f:
        requirements = []
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                requirements.append(line)
        return requirements


# Read core dependencies from requirements.txt
install_requires = read_requirements("requirements.txt")

# Development dependencies
dev_requires = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "pre-commit>=3.0.0",
    "ipython>=8.0.0",
    "ipykernel>=6.0.0",
]

setup(
    name="tensorfi-sharpe",
    version="0.1.15",
    description="Financial data access and analysis library with market data, options calculations, and database integration",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="rwang",
    author_email="",  # Add your email if desired
    url="https://github.com/wang-sanity/sharpe",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "all": install_requires + dev_requires,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="finance, markets, data, options, database, analysis",
    project_urls={
        "Documentation": "https://github.com/wang-sanity/sharpe/docs",
        "Source": "https://github.com/wang-sanity/sharpe",
        "Tracker": "https://github.com/wang-sanity/sharpe/issues",
    },
)
