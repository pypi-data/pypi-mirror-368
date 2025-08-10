"""Setup script for quantumsim-edu package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quantumsim-edu",
    version="2.0.1",
    author="Vaiditya Tanwar", 
    author_email="vaidityatanwar2207@gmail.com",
    description="Educational quantum computing simulator with statevector simulation, quantum algorithms, and noise modeling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vaiditya2207/quantum-projects",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "isort",
            "mypy",
        ],
        "jupyter": [
            "jupyterlab>=3.0",
            "ipywidgets>=7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "quantumsim=quantumsim.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Vaiditya2207/quantum-projects/issues",
        "Source": "https://github.com/Vaiditya2207/quantum-projects",
        "Documentation": "https://github.com/Vaiditya2207/quantum-projects/blob/main/README.md",
    },
)
