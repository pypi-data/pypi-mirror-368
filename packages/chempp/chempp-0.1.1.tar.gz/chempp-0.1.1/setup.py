
from setuptools import setup, find_packages
import os

# Read version from package
version_ns = {}
with open(os.path.join("chempp", "version.py")) as f:
    exec(f.read(), version_ns)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chempp",
    version=version_ns.get("__version__", "0.1.1"),
    author="Your Name or Team",
    author_email="you@example.com",
    description="Chem++: domain-specific language and runtime for computational chemistry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/chempp",
    packages=find_packages(exclude=["tests", "docs"]),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "aiohttp>=3.7.4",
    ],
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
)
