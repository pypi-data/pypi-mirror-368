
from setuptools import setup, find_packages

setup(
    name="ncpy",
    version="0.1.0",
    author="Your Name",
    author_email="you@example.com",
    description="A Python package for numerical methods",
    packages=find_packages(),
    install_requires=["numpy", "scipy"],
    python_requires=">=3.6",
)
