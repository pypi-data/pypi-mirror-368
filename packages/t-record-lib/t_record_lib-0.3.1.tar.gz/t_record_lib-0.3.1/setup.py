#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

install_requirements = open("requirements.txt").readlines()

setup(
    author="Thoughtful",
    author_email="support@thoughtful.ai",
    python_requires=">=3.11",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    description="""Cookiecutter template for Thoughtful pip package""",  # noqa: E501
    long_description=readme,
    keywords="t_record",
    name="t_record_lib",
    packages=find_packages(include=["t_record", "t_record.*"]),
    test_suite="tests",
    url="https://www.thoughtful.ai/",
    version="0.3.1",
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requirements,
)
