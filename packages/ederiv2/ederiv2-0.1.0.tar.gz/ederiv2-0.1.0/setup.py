from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A molecular graph generation and analysis toolkit using Graph Neural Networks"

# Read requirements from requirements.txt
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    return requirements

setup(
    name="ederiv2",
    version="0.1.0",
    author="eDeriv2 Team",
    author_email="your.email@example.com",
    description="A molecular graph generation and analysis toolkit using Graph Neural Networks",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/eDeriv2",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/eDeriv2/issues",
        "Source": "https://github.com/yourusername/eDeriv2",
        "Documentation": "https://github.com/yourusername/eDeriv2#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
        "full": [
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
            "ipython>=7.0.0",
            "jupyter>=1.0.0",
            "notebook>=6.4.0",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["*.py", "**/*.py", "**/*.sdf", "**/*.csv", "**/*.pkl"],
    },
    entry_points={
        "console_scripts": [
            "ederiv2=src.cli:main",
        ],
    },
    keywords="molecular-graphs, graph-neural-networks, chemistry, machine-learning, drug-discovery",
    license="MIT",
)