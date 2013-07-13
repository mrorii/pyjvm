#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "pyjvm",
    version = "0.0.0",
    author = "Naoki Orii",
    author_email = "naoki.orii@gmail.com",
    url = "https://github.com/mrorii/pyjvm",
    description = "Yet another Java virtual machine, written in pure python",
    platforms = "any",
    packages=['pyjvm'],
    package_dir={"pyjvm":"pyjvm"},
    keywords = "jvm",
    classifiers = [
        "Programming Language :: Java",
        "Programming Language :: Python",
    ],
    scripts = ['bin/pyjvm'],
)
