from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="mtrust-medical",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="M-TRUST: Bias detection and mitigation for medical AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mtrust-medical",
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
        "Bug Reports": "https://github.com/yourusername/mtrust-medical/issues",
        "Source": "https://github.com/yourusername/mtrust-medical",
        "Paper": "https://arxiv.org/abs/your-paper-id",
    },
)