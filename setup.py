import os
from setuptools import setup, find_packages


def read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    file = open(filepath, "r")
    return file.read()


setup(
    name="Open-Source-Software",
    version="0.0.1",
    author="Rohan Malavathu, Vishal Muthuraja, Dev Thakkar",
    author_email="rmalavat@purdue.edu, vmuthura@purdue.edu, dthakka9@purdue.edu",
    description="",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="MIT License",
    keywords=[],
    url="",
    packages=find_packages(),
    scripts=[],
    install_requires=read("requirements.txt").splitlines(),
    include_package_data=True,
    zip_safe=False,
)