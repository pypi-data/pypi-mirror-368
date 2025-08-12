from setuptools import setup, find_packages

import re
version = re.search(
    '^__version__\s*=\s*"(.*)"', open("rapyuta_io/__init__.py").read(), re.M
).group(1)

with open("README.md", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="rapyuta_io",
    version=version,
    description="Rapyuta.io Python SDK",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Rapyuta Robotics",
    author_email="opensource@rapyuta-robotics.com",
    packages=find_packages(include=["rapyuta_io*"]),
    python_requires=">=3.8",
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
        "requests>=2.20.0",
        "six>=1.16.0",
        "urllib3>=1.23",
        "python-dateutil>=2.8.2",
        "pytz",
        "pyyaml>=5.4.1",
        "setuptools",
    ],
    extras_require={
        "dev": ["sphinx", "furo"],
        "test": [
            "testtools",
            "pyfakefs",
            "mock",
        ],
    },
)
