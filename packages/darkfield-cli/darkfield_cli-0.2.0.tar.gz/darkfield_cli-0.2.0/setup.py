from setuptools import setup, find_packages

setup(
    name="darkfield",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "rich>=13.0",  # For beautiful CLI output
        "pydantic>=2.0",
        "python-dotenv>=1.0",
        "keyring>=24.0",  # For secure credential storage
        "tabulate>=0.9",
        "tqdm>=4.65",  # Progress bars
        "websocket-client>=1.5",  # For real-time monitoring
        "chardet>=5.0",  # For encoding detection
        "pandas>=2.0",  # For data processing
        "tenacity>=8.0",  # For retry logic
    ],
    extras_require={
        "llm": [
            "openai>=1.0",  # For OpenAI GPT models
            "anthropic>=0.5",  # For Anthropic Claude models
        ]
    },
    entry_points={
        "console_scripts": [
            "darkfield=darkfield_cli.main:cli",
        ],
    },
    python_requires=">=3.8",
    author="Darkfield AI",
    author_email="support@darkfield.ai",
    description="CLI for Darkfield ML Safety Platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/darkfield-ai/darkfield-cli",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)