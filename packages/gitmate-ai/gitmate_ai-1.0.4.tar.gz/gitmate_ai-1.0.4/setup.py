from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitmate-ai",
    version="1.0.4",
    description="GitMate - AI Git Assistant for Terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",  
    author="Tejas Raundal",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gitmate=gitmate.cli:main',
        ],
    },
    install_requires=[
        "rich",
        "langchain",
        "langchain-google-genai",
        "langchain-openai",
        "langchain-anthropic",
    ],
    python_requires='>=3.8',
)
