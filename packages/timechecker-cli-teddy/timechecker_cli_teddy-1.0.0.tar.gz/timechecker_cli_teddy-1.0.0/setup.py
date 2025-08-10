"""Setup script for timechecker package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="timechecker-cli-teddy",
    version="1.0.0",
    author="Timechecker Team",
    author_email="team@timechecker.dev",
    description="CLI tool for checking current time in different timezones",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timechecker/timechecker",
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
    ],
    python_requires=">=3.7",
    install_requires=[
        "pytz>=2023.3",
    ],
    entry_points={
        "console_scripts": [
            "tmt=timechecker.cli:main",
        ],
    },
)