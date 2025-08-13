import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = "2.0a8"

setuptools.setup(
    name="pycentral",
    version=VERSION,
    author="aruba-automation",
    author_email="aruba-automation@hpe.com",
    description="HPE Aruba Networking Central Python Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aruba/pycentral",
    packages=setuptools.find_packages(exclude=["docs", "tests", "sample_scripts"]),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests==2.32.4",
        "PyYAML==6.0.2",
        "oauthlib==3.2.2",
        "requests_oauthlib==2.0.0",
        "pytz==2025.2",
    ],
    extras_require={"colorLog": ["colorlog"]},
)
