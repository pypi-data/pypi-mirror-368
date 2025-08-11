from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="games-hitesh14",
    version="1.0.0",
    description="A collection of fun games: Bulls and Cows, Guess the Number, Rock Paper Scissors.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hitesh",
    url="https://github.com/hitesh14/games", 
    packages=find_packages(exclude=["tests*", "docs"]),
    install_requires=[],
    python_requires=">=3.6",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Intended Audience :: End Users/Desktop",
    ],
    keywords=["games", "fun", "bulls and cows", "guess the number", "rock paper scissors"],
)