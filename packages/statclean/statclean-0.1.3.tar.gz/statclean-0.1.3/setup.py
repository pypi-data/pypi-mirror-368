from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="statclean",
    version="0.1.3",
    author="Subashanan Nair",
    author_email="subaashnair12@gmail.com",
    description="A comprehensive statistical data preprocessing and outlier detection library with formal statistical testing and publication-quality reporting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SubaashNair/StatClean",
    project_urls={
        "Homepage": "https://subaashnair.github.io/StatClean/",
        "Documentation": "https://subaashnair.github.io/StatClean/",
        "Source": "https://github.com/SubaashNair/StatClean",
        "Tracker": "https://github.com/SubaashNair/StatClean/issues",
        "API Reference": "https://subaashnair.github.io/StatClean/api-reference",
        "Examples": "https://subaashnair.github.io/StatClean/examples",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.2.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "scipy>=1.6.0",
        "tqdm>=4.60.0",
    ],
)