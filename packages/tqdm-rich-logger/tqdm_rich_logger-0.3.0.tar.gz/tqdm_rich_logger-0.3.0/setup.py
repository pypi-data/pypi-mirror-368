from setuptools import setup, find_packages

setup(
    name="tqdm-rich-logger",
    version="0.3.0",
    author="Madhav Arora",
    author_email="your.email@example.com",
    description="TQDM-safe Rich logger with file output and exception catching",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/madhavarora03/tqdm-rich-logger",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "rich>=13.0.0",
        "tqdm>=4.0.0",
    ],
)
