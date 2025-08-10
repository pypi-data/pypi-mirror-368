from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tmt-timezone",
    version="1.0.0",
    author="TMT Developer",
    author_email="dev@tmt.com",
    description="A CLI tool to get current time in different timezones",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tmt/tmt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pytz>=2021.1",
    ],
    entry_points={
        "console_scripts": [
            "tmt=tmt.cli:main",
        ],
    },
)