from setuptools import setup, find_packages

setup(
    name="fartlib",
    version="2.0.0",
    author="Adonis",
    description="the official fartlib package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/adondonis/fartlib",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
