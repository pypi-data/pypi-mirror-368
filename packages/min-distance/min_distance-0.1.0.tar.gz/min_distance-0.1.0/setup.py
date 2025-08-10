from setuptools import setup, find_packages

setup(
    name="min_distance",
    version="0.1.0",
    author="Vansh",
    author_email="vanshbhardwajhere@gmail.com",
    description="A simple Python package to calculate the minimum distance between two geographic points",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vanshbhardwajhere/min_distance",  # Replace with your repo URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
