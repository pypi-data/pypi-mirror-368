from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llmuxer",
    version="0.1.0",
    author="Mihir Ahuja",
    author_email="mihirahuja09@gmail.com",
    description="Automatically find cheaper LLM alternatives while maintaining performance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mihirahuja1/llmuxer",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "tqdm>=4.60.0",
        "openai>=1.0.0",
        "anthropic>=0.5.0",
    ],
    extras_require={
        "dev": ["pytest>=6.0", "black", "flake8", "mypy", "isort"],
        "data": ["pandas>=1.3.0", "datasets>=2.0.0"],
    },
)