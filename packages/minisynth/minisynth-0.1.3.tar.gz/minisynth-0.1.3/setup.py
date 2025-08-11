from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="minisynth",
    version="0.1.3",
    author="inspektral",
    description="A Python-based modular synthesizer framework for generating audio and datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/inspektral/minisynth",
    packages=["minisynth"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
    ],
)