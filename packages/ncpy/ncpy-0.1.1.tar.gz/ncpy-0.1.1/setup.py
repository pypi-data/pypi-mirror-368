from setuptools import setup, find_packages
import pathlib

# Read the contents of README.md
this_dir = pathlib.Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="ncpy",
    version="0.1.1",  # bump version for new release
    author="M. Almas",
    author_email="mkhan@cs.qau.edu.pk",
    description="A Python package for numerical computing, including root-finding, interpolation, integration, differentiation, and linear system solvers.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # tells PyPI to render Markdown
    packages=find_packages(),
    install_requires=["numpy", "scipy"],
    python_requires=">=3.6",
)
