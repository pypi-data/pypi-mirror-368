# coding: utf-8
"""
@software: PyCharm
@author: Lionel Johnson
@contact: https://fairy.host
@organization: https://github.com/FairylandFuture
@datetime: 2024-05-09 16:38:27 UTC+08:00
"""

import os
import subprocess
import sys
import tomllib
from datetime import datetime
from enum import StrEnum
from typing import Optional

import requests
import setuptools

_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

if sys.version_info < (3, 11):
    sys.exit("Python 3.11 or higher is required.")


class InstallDependenciesCommand(setuptools.Command):
    user_options = []

    def initialize_options(self):
        return

    def finalize_options(self):
        return

    def run(self):
        command = "python -m pip install --force git+https://github.com/imba-tjd/pip-autoremove@ups"
        subprocess.call(command, shell=True)


class VersionLevelEnum(StrEnum):
    release = "release"  # 发布版本
    test = "test"  # 测试版本
    alpha = "alpha"  # 内测版本
    beta = "beta"  # 公测版本


class Package(object):

    def __init__(self, version_level: Optional[VersionLevelEnum] = None):
        self.version_number: str = self._version()
        self.version_level: VersionLevelEnum = version_level if version_level else VersionLevelEnum.release

    @property
    def name(self):
        return "PyFairylandFuture"

    @property
    def version(self):
        serial_number = self.github_commit_number()

        if self.version_level == VersionLevelEnum.release:
            version = self.version_number
        elif self.version_level == VersionLevelEnum.test:
            version = f"{self.version_number}rc.{serial_number}"
        elif self.version_level == VersionLevelEnum.alpha:
            version = f"{self.version_number}alpha.{serial_number}"
        elif self.version_level == VersionLevelEnum.beta:
            version = f"{self.version_number}beta.{serial_number}"
        else:
            raise RuntimeError("Unsupport version level, Please select from `VersionLevelEnum`.")

        return version

    @property
    def author(self):
        return "Lionel Johnson"

    @property
    def email(self):
        return "fairylandfuture@protonmail.com"

    @property
    def description(self):
        return "Efficient developed Python library."

    @property
    def url(self):
        return "https://github.com/FairylandTech/pypi-fairylandfuture"

    @property
    def license(self):
        return "AGPLv3+"

    @property
    def long_description(self):
        with open(os.path.join(_ROOT_PATH, "README.md"), "r", encoding="UTF-8") as stream:
            content = stream.read()

        return content

    @property
    def long_description_content_type(self):
        return "text/markdown"

    @property
    def packages_include(self):
        include = ("fairylandfuture", "fairylandfuture.*")

        return include

    @property
    def packages_exclude(self):
        exclude = (
            "bin",
            "conf",
            "docs",
            "scripts",
            "temp",
            "test",
        )

        return exclude

    @property
    def packages_data(self):
        data = {"": ["*.txt", "*.rst", "*.md"], "fairylandfuture": ["conf/**"]}

        return data

    @property
    def fullname(self):
        return self.name + self.version

    @property
    def python_requires(self):
        return ">=3.11"

    @property
    def keywords(self):
        return [
            "fairyland",
            "Fairyland",
            "pyfairyland",
            "PyFairyland",
            "fairy",
            "Fairy",
            "fairylandfuture",
            "PyFairylandFuture",
            "FairylandFuture",
        ]

    @property
    def include_package_data(self):
        return True

    @property
    def classifiers(self):
        results = [
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",
            "Programming Language :: SQL",
            "Framework :: Django :: 4",
            "Framework :: Django :: 5",
            "Framework :: Flask",
            "Framework :: FastAPI",
            "Framework :: Flake8",
            "Framework :: IPython",
            "Framework :: Jupyter",
            "Framework :: Scrapy",
            "Natural Language :: English",
            "Natural Language :: Chinese (Simplified)",
            "Operating System :: Microsoft :: Windows :: Windows 10",
            "Operating System :: Microsoft :: Windows :: Windows 11",
            "Operating System :: POSIX :: Linux",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Software Development :: Libraries :: Application Frameworks",
            "Topic :: Software Development :: Version Control :: Git",
            "Topic :: System :: Operating System Kernels :: Linux",
            "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        ]

        return results

    @property
    def install_requires(self):
        with open("pyproject.toml", "rb") as stream:
            data = tomllib.load(stream)

        requirements = data.get("project", {}).get("dependencies", [])

        return requirements

    @staticmethod
    def github_commit_number():

        def local_build_version():
            try:
                with open(os.path.join(_ROOT_PATH, "fairylandfuture", "conf", "release", "buildversion"), "r", encoding="UTF-8") as stream:
                    content = stream.read()
                return content
            except Exception as err:
                print(f"Error: Getting build version {err}")
                return 0

        try:
            url = "https://raw.githubusercontent.com/FairylandTech/pypi-fairylandfuture/ReleaseMaster/fairylandfuture/conf/release/buildversion"
            response = requests.get(url)
            response.raise_for_status()

            return response.text
        except Exception as err:
            print(err)
            return local_build_version()

    @staticmethod
    def _version():
        try:
            with open(os.path.join(_ROOT_PATH, "pyproject.toml"), "rb") as stream:
                data = tomllib.load(stream)
            return data.get("project", {}).get("version", "0.0.0")
        except Exception as err:
            print(f"Error: Getting version {err}")
            raise RuntimeError("Failed to get version.")


if __name__ == "__main__":
    package = Package(VersionLevelEnum.release)
    setuptools.setup(
        name=package.name,
        version=package.version,
        author=package.author,
        author_email=package.email,
        description=package.description,
        url=package.url,
        license=package.license,
        packages=setuptools.find_packages(include=package.packages_include),
        package_data=package.packages_data,
        include_package_data=package.include_package_data,
        classifiers=package.classifiers,
        python_requires=package.python_requires,
        install_requires=package.install_requires,
        # cmdclass=package.cmdclass,
        fullname=package.fullname,
        keywords=package.keywords,
        long_description=package.long_description,
        long_description_content_type=package.long_description_content_type,
    )
