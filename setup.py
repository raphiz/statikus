#!/usr/bin/env python
# encoding: utf-8

import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


setup(
    name="statikus",
    version="0.1.0.dev0",
    packages=['statikus'],
    author="Raphael Zimmermann",
    author_email="dev@raphael.li",
    url="https://github.com/raphiz/statikus",
    description="Like flask - but for static sites",
    long_description=("For more information, please checkout the `Github Page "
                      "<https://github.com/raphiz/statikus>`_."),
    license="MIT",
    platforms=["Linux", "BSD", "MacOS"],
    include_package_data=True,
    zip_safe=False,
    install_requires=open('./requirements.txt').read(),
    tests_require=open('./requirements-dev.txt').read(),
    cmdclass={'test': PyTest},
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        "Programming Language :: Python :: Implementation :: CPython",
        'Development Status :: 4 - Beta',
    ],
)
