from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="seedling",
    version="0.1.0",
    description="Seed library management system",
    author="Chris Malek",
    author_email="cmalek@placodermi.org",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "htmlcov"]),
    include_package_data=True,
    url="https://github.com/cmalek/seedling",
    keywords=['django'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
