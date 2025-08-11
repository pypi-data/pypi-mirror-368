#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="jarvis-meme-generator",
    version="1.0.1",
    author="Joey Bejjani",
    author_email="jbejjani2022@gmail.com",
    description="Generate custom Jarvis memes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jbejjani2022/jarvis-meme-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
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
        "Pillow>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "jarvis=jarvis_generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["static/jarvis.png"],
    },
    zip_safe=False,
)