from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="italica",
    version="1.0.0",
    author="7vntii",
    author_email="jj9dptr57@mozmail.com",
    description="A simple library for adding markdown-style formatting to print and input functions",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/7vntii/italica",
    project_urls={
        "Bug Reports": "https://github.com/7vntii/italica/issues",
        "Source": "https://github.com/7vntii/italica",
        "Documentation": "https://github.com/7vntii/italica#readme",
    },
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    keywords="markdown, formatting, print, input, italic, bold, terminal, console",
    include_package_data=True,
    zip_safe=False,
)
