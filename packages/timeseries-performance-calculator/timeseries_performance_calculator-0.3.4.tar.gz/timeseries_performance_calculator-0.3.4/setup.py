from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
requirements_path = os.path.join(here, 'requirements.txt')

with open(requirements_path) as f:
    requirements = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

setup(
    name="timeseries_performance_calculator",
    version="0.3.4",
    packages=find_packages(),
    install_requires=requirements,
    author="June Young Park",
    author_email="juneyoungpaak@gmail.com",
    description="A Python package for calculating and analyzing time series performance metrics",
    long_description=open("README.md", encoding="utf-8").read() if open("README.md", encoding="utf-8", errors='ignore') else "",
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Office/Business :: Financial",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
    ],
)
