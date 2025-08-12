from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="possinote",
    version="1.0.0",
    author="PossiNote Team",
    author_email="support@possitech.net",
    description="Official Python SDK for PossiNote API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/possitech/possinote-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/possitech/possinote-python/issues",
        "Source": "https://github.com/possitech/possinote-python",
        "Documentation": "https://possitech.net/api-docs",
    },
)
