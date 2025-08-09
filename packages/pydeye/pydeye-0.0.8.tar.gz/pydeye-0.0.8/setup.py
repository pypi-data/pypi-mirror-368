#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pydeye",
    version="0.0.8",
    description="Python deye inverter interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jakob Salmič",
    author_email="salmic.jakob@gmail.com",
    maintainer=", ".join(("Jakob Salmič <salmic.jakob@gmail.com>",)),
    license="GPL",
    url="https://github.com/UnknownHero99/pydeye",
    python_requires=">=3.8",
    packages=find_packages(),
    keywords=["homeautomation", "deye", "inverter", "modbus", "solar"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Home Automation",
    ],
    install_requires=["pymodbus"],
)
