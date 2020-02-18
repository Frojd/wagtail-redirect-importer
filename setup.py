#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from wagtail_redirect_importer/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("wagtail_redirect_importer", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

with open('README.md') as f:
    readme = f.read()

# Convert markdown to rst
try:
    from pypandoc import convert
    long_description = convert("README.md", "rst")
except:  # NOQA
    long_description = ""

setup(
    name='wagtail_redirect_importer',
    version=version,
    description="""Lets you build import redirects in django""",
    long_description=long_description,
    author='Fröjd',
    author_email='martin@marteinn.se',
    url='https://github.com/Frojd/wagtail-redirect-importer',
    packages=[
        'wagtail_redirect_importer',
    ],
    include_package_data=True,
    install_requires=[
        'tablib[xls,xlsx]',
    ],
    license="MIT",
    zip_safe=False,
    keywords='wagtail_redirect_importer',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 2',
    ],
)
