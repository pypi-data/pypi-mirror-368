from setuptools import setup, find_packages

setup(
    name="bilateral-truth",
    version="0.1.0", 
    description="Caching bilateral factuality evaluation using generalized truth values",
    author="Bradley Allen",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",  # For OpenAI API and OpenRouter
        "anthropic>=0.3.0",  # For Anthropic Claude API
        "requests>=2.25.0",  # For HTTP requests to other APIs
        "python-dotenv>=0.19.0",  # For .env file support
    ],
    entry_points={
        'console_scripts': [
            'bilateral-truth=bilateral_truth.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)