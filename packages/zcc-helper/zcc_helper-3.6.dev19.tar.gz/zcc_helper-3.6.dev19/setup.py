"""A setuptools based setup module."""

import pathlib
from setuptools import setup, find_packages

from zcc.constants import NAME, VERSION


# The text of the README file
README = (pathlib.Path(__file__).parent / "README.md").read_text()

setup(
    name=NAME,
    version=VERSION,
    description="ZIMI ZCC helper module",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Mark Hannon",
    author_email="mark.hannon@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    project_urls={"Source": "https://bitbucket.org/mark_hannon/zcc"},
    install_requires=[""],
)
