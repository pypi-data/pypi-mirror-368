#!/usr/bin/env python3
"""Build the Nornir-Collection Python Package with setuptools"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="nornir-collection",
    version="0.0.31",
    author="Willi Kubny",
    author_email="willi.kubny@gmail.ch",
    description="Nornir-Collection contains network automation functions and complete IaC workflows with \
        Nornir and other python libraries. It contains Nornir tasks and general functions in Nornir style.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.9",
)
