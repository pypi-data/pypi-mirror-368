import os
from setuptools import setup, find_packages

# Read the contents of your README file in a more robust way
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Change the name to match the GitHub repository for consistency
    name="project-bootstrapper",
    version="0.1.1",  # Bump the version to indicate a new release with this fix

    # This is the most critical fix: be explicit about the packages.
    # It tells setuptools exactly what to include.
    packages=["bootstrapper"],

    # Add any external dependencies here. For now, it's empty.
    install_requires=[],

    entry_points={
        "console_scripts": [
            "bootstrapper=bootstrapper.cli:main",
        ],
    },

    author="Yeke Daniel",
    author_email="Danielyeke489@gmail.com",
    description="A CLI tool to bootstrap Python projects with Git and venv support.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Danny26y/python-cli-bootstrapper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)