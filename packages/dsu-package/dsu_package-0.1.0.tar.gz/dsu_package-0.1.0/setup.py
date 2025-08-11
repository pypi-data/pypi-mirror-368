from setuptools import setup, find_packages

setup(
    name="dsu_package",
    version="0.1.0",
    author="Charuvarthan",
    author_email="charuvarthan05@gmail.com",
    description="Disjoint Set Union (Union-Find) data structure with path compression and union by size",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
