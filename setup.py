# -*- coding: utf-8 -*-

"""Setup script for the Flight Tower Engine."""

import os

from setuptools import find_packages, setup


def read_file(file_name: str) -> str:
    """Read file and return its content.

    :param file_name: Name of file to be read (at root level).
    :return: Content of file, unprocessed.

    """
    with open(file_name, "r") as file_:
        return file_.read()


def get_build_version():
    """Get build version for creating wheel.

    When publishing python package, the version number has to be unique
    Let's leverage the Azure Pipeline build number
    to get a unique third digit in the release
    First two digits remain specified in code
    If we are not in the context of a Azure Devops pipeline, return a default value
    """
    return os.getenv("Build.BuildNumber", default=0)


setup(
    name="log_sorting",
    version=f"1.0.{get_build_version()}",
    description="Code for log sorting statistics.",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    #url="https://sodra.visualstudio.com/Sodra/_git/Sodra.Common.FlightTower",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.8",
    ],
    keywords=["log", "sorting"],
    packages=find_packages(exclude=("tests",)),
    platforms=["Any"],
    python_requires=">=3.8.*",
    install_requires=read_file("requirements.txt").splitlines(),
    #extras_require={"dev": read_file("requirements-dev.txt").splitlines()},
    entry_points={
        "console_scripts": [
            "flight = flight_tower.__main__:main",
        ],
    },
    #project_urls={
    #    "Source": "https://sodra.visualstudio.com/Sodra/_git/Sodra.Common.FlightTower",
    #},
    license="Other/Proprietary",
)
