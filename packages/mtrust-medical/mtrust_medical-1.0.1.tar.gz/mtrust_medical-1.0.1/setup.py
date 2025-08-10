from setuptools import setup, find_packages
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

def read_file(filename):
    """Read a file and return its content."""
    filepath = os.path.join(current_dir, filename)
    with open(filepath, "r", encoding="utf-8") as fh:
        return fh.read()

def read_requirements():
    """Read requirements from requirements.txt."""
    content = read_file("requirements.txt")
    return [line.strip() for line in content.splitlines() if line.strip() and not line.startswith('#')]

long_description = read_file("README.md")
requirements = read_requirements()

setup(
    name="mtrust-medical",
    version="1.0.1",
    author="Nasim Mahmud Nayan",
    author_email="smnoyan670@gmail.com",
    description="M-TRUST: Bias detection and mitigation for medical AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NMNayan57/mtrush_medical.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=7.0", "black>=22.0", "flake8>=4.0"],
        "viz": ["matplotlib>=3.5", "seaborn>=0.11"],
    },
    entry_points={
        "console_scripts": [
            "mtrust=mtrust.cli:main",
        ],
    },
    keywords="medical ai bias fairness healthcare trustworthy",
    project_urls={
        "Bug Reports": "https://github.com/NMNayan57/mtrush_medical/issues",
        "Source": "https://github.com/NMNayan57/mtrush_medical",
    },
)