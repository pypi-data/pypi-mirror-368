from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="min_distance",
    version="1.0.0",
    author="Vansh",
    author_email="vanshbhardwajhere@gmail.com",
    description="A simple Python package to calculate the minimum distance between two geographic points",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vanshbhardwajhere/min_distance",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
