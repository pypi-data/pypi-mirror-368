# FILE 2: setup.py (Package Configuration)

from setuptools import setup, find_packages

# Read README for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "DOME - Natural Language Programming"

setup(
    name="e-dome",
    version="2.0.0",
    author="e-dome.dev",
    author_email="contact@e-dome.dev",
    description="DOME - Natural Language Programming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dome",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/dome/issues",
        "Source Code": "https://github.com/yourusername/dome",
    },
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
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "full": [
            "pandas>=1.3.0",
            "numpy>=1.20.0",
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
            "scikit-learn>=1.0.0",
        ],
    },
    keywords="natural-language-programming, code-generation, nlp, python",
    entry_points={
        "console_scripts": [
            "dome=dome:start",
        ],
    },
)
