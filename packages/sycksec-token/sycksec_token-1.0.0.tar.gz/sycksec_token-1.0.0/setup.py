from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="sycksec-token",
    version="1.0.0",
    author="Arjun Mani",
    author_email="arjunmani45.mm@gmail.com",
    description="Secure token generation and verification engine with rate limiting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sycksec/sycksec-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "test": ["pytest>=6.0", "pytest-cov>=2.0"],
    },
    entry_points={
        "console_scripts": [
            "sycksec-cli=sycksec.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)