"""Setup script for clasherjk package."""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements directly
requirements = ["httpx>=0.24.0"]

setup(
    name="clasherjk",
    version="1.0.0",
    author="ClasherJK",
    author_email="your.email@example.com",
    description="A Python library for Clash of Clans API using secure proxy server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clasherjk/clasherjk-python",
    project_urls={
        "Documentation": "https://github.com/clasherjk/clasherjk-python#readme",
        "Source": "https://github.com/clasherjk/clasherjk-python",
        "Tracker": "https://github.com/clasherjk/clasherjk-python/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords=[
        "clash-of-clans",
        "coc",
        "api",
        "wrapper",
        "supercell",
        "mobile-game",
        "gaming",
        "clasherjk"
    ],
    include_package_data=True,
    zip_safe=False,
)