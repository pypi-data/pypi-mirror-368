from setuptools import setup, find_packages

setup(
    name="marchantia_cv_root",
    version="0.0.2",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)