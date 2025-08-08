from setuptools import setup, find_packages

setup(
    name="githubanalysis",
    version="0.1.6",
    packages=find_packages(),
    package_data={
        'githubanalysis': ['llm/prompts/*.json'],
    },
    include_package_data=True,
    install_requires=[
        "gitpython>=3.1.42",
        "numpy>=1.23.0",
        "scikit-learn>=1.2.0",
        "nltk>=3.8.0",
        "requests>=2.28.0",
        "openai>=1.0.0",
        "tiktoken>=0.5.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.65.0",
        "markdown>=3.3.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ],
    entry_points={
        'console_scripts': [
            'githubanalysis=githubanalysis.cli:main',
        ],
    },
    author="Rimon",
    author_email="info@rimon.com.au",
    description="A powerful tool for analyzing Git repositories using LLM-powered insights",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="git, analysis, repository, llm, openai, gpt, commit, log, analysis",
    python_requires=">=3.7",
    zip_safe=False,
) 