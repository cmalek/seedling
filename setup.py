from setuptools import setup, find_packages


setup(name="seedling",
      version="0.1.0",
      description="Seed library management system",
      author="Chris Malek",
      author_email="cmalek@placodermi.org",
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "htmlcov"])
      )
