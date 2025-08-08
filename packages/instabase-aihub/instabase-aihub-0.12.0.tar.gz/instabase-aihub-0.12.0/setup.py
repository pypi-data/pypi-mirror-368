# coding: utf-8

"""
    AIHub API

    The AIHub REST API. Please see https://aihub.instabase.com/docs/aihub/ for more details.
    Contact: support@instabase.com

"""  # noqa: E501


from setuptools import setup, find_packages  # noqa: H301
import json

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools
NAME = "instabase-aihub"
VERSION = json.loads(open("../config.json").read())["packageVersion"]
PYTHON_REQUIRES = ">=3.7"
REQUIRES = [
    "urllib3 >= 1.25.3, < 2.1.0",
    "python-dateutil",
    "pydantic >= 2",
    "typing-extensions >= 4.7.1",
]

setup(
    name=NAME,
    version=VERSION,
    description="AI Hub API",
    author="Instabase Support",
    author_email="support@instabase.com",
    url="https://docs.instabase.com",
    keywords=["Instabase", "AI Hub API"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    license="MIT",
    long_description_content_type='text/markdown',
    long_description=open("README.md").read(),
    package_data={"aihub": ["py.typed"]},
)
