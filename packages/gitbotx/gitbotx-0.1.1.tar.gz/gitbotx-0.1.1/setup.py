from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitbotx",  # must be unique on PyPI
    version="0.1.1",
    author="Parikshit Sonwane",
    author_email="parik.sonwane06@gmail.com",
    description="A smart CLI tool to automate git workflows and suggest commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parikshit-06/gitbotx",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'gitbotx=gitbotx.cli:main',
        ],
    },
)