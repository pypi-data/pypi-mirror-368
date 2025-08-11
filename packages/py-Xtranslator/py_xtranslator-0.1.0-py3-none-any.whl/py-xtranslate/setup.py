# setup.py
from setuptools import setup, find_packages

setup(
    name="py-Xtranslator",
    version="0.1.0",
    author="ALI",
    author_email="thealiapi@gmail.com",
    description="Simple Python translation library using Google Translate unofficial API.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/iTs-GoJo/py-Xtranslator",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
