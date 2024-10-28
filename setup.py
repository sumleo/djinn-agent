from setuptools import find_packages, setup

setup(
    name="djinn-agent",
    version="0.1.0",
    description="A lightweight, terminal-based tool for seamless interaction with Claude's advanced computer-use capabilities.",
    author="Yi Liu, Gelei Deng and Yuekang Li",
    author_email="yi@quantstamp.com",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "djinn-agent=djinn.main:sync_main",
        ],
    },
    install_requires=[
        "streamlit>=1.38.0",
        "anthropic[bedrock,vertex]>=0.37.1",
        "jsonschema==4.22.0",
        "boto3>=1.28.57",
        "google-auth<3,>=2",
        "ruff==0.6.7",
        "pre-commit==3.8.0",
        "pytest==8.3.3",
        "pytest-asyncio==0.23.6",
        "rich",
    ],
)
