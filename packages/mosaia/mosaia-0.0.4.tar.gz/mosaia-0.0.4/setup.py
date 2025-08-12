from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mosaia",
    version="0.0.4",
    author="Mosaia Team",
    author_email="support@mosaia.ai",
    description="A comprehensive Python SDK for the Mosaia AI platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mosaia-development/mosaia-python-sdk",
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.8.0",
        "dataclasses-json>=0.5.0; python_version < '3.7'",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'isort>=5.10.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
        ],
        # 'docs': [
        #     'sphinx>=5.0.0',
        #     'sphinx-rtd-theme>=1.0.0',
        # ],
    },
    keywords="ai, artificial intelligence, api, sdk, mosaia, agents, tools, applications",
    project_urls={
        "Bug Reports": "https://github.com/mosaia-development/mosaia-python-sdk/issues",
        "Source": "https://github.com/mosaia-development/mosaia-python-sdk",
        "Documentation": "https://docs.mosaia.ai/python-sdk",
    },
) 