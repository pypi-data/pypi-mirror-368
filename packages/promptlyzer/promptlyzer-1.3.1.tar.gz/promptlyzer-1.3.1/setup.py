from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="promptlyzer",
    version="1.3.1",
    description="Official Python SDK for Promptlyzer - Smart prompt management and multi-provider LLM inference optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Promptlyzer",
    author_email="contact@promptlyzer.com",
    url="https://promptlyzer.com",
    project_urls={
        "Homepage": "https://promptlyzer.com",

    },
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "openai>=1.0.0",
        "anthropic>=0.15.0",
        "nest-asyncio>=1.5.6",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
)