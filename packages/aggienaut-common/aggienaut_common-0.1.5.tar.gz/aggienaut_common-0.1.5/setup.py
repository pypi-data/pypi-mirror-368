from setuptools import setup, find_packages
import os

# Read the long description from README
def read_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()

setup(
    name="aggienaut-common",
    version="0.1.0",
    author="AggieNaut Team",
    author_email="your-email@example.com",  # Update with actual email
    description="A collection of common utilities and modules for AggieNaut projects",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Aggienaut-Apps/aggienaut-common",
    project_urls={
        "Bug Tracker": "https://github.com/Aggienaut-Apps/aggienaut-common/issues",
        "Source Code": "https://github.com/Aggienaut-Apps/aggienaut-common",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # Update if different
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "paho-mqtt>=1.6.0",
        "pyserial>=3.5",
        "toml>=0.10.2",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    include_package_data=True,
    package_data={
        "common": ["../default_config_files/*.toml"],
    },
)