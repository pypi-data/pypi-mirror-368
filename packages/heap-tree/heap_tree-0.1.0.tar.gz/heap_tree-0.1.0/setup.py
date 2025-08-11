from setuptools import setup, find_packages

setup(
    name="heap-tree",  # pip install heap-tree
    version="0.1.0",
    author="Visal",
    author_email="you@example.com",
    description="A simple heap data structure implementation in Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/itsHellboyHere/Heap",  # GitHub repo
    packages=find_packages(),
    python_requires=">=3.6",
)
