from setuptools import setup

setup(
    name="letrbinr",
    version="1.0.6",
    author="Vitek",
    author_email="cheeseqwertycheese@gmail.com",
    description="A toy esoteric language",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Viktor640266/letrbinr",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    packages = ["letrbinr"]
)
