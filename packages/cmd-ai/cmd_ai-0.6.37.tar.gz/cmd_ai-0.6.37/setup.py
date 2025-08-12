#!/usr/bin/env python3
import os

from setuptools import find_packages, setup


# -----------problematic------
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


import os.path


def readver(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in readver(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name="cmd_ai",
    description="Another ChatGTP project in commandline of linux",
    author="jaromrax",
    url="http://gitlab.com/me/cmd_ai",
    author_email="jaromrax@gmail.com",
    license="GPL2",
    version=get_version("cmd_ai/version.py"),
    packages=["cmd_ai"],
    package_data={"cmd_ai": ["data/*"]},
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    scripts=["bin/cmd_ai", "bin/aigui"],
    install_requires=["fire", "console", "click", "pandas", "openai", "prompt_toolkit","googlesearch-python","unidecode", "anthropic",  "google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib" ,"tiktoken","selenium", "beautifulsoup4", "sympy" ,"webdriver-manager","Pillow","gTTs", "google.genai", "playwright"]
)
