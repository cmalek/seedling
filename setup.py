from setuptools import setup, find_packages


setup(name="multitenant",
      version="1.3.8",
      description="Wagtail Multitenant",
      author="ADS",
      author_email="imss-ads-staff@caltech.edu",
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "htmlcov"])
      )
