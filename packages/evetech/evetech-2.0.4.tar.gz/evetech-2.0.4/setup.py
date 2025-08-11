from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="evetech",
    version="2.0.4",
    author="ratouney",
    author_email="contact@ratouney.dev",
    description="EVE Online ESI OAuth handler with multi-character support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/evetech",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0",
    ],
)