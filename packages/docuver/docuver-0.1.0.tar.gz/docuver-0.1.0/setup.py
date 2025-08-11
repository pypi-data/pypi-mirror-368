#!/usr/bin/env python3
"""
Copyright (C) 2025, Jabez Winston C

Setup script for Docuver - Document Version Control Tool

Author  : Jabez Winston C <jabezwinston@gmail.com>
License : MIT
Date    : 10 Aug 2025

"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
        return f.read()

# Read version from __init__.py
def read_version():
    version_file = os.path.join(os.path.dirname(__file__), 'docuver', 'version.py')
    with open(version_file, encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

setup(
    name='docuver',
    version=read_version(),
    author='Jabez Winston C',
    author_email='jabezwinston@gmail.com',
    description='A meta tool for version control of Office documents (docx, xlsx, pptx, odt, ods, odp)',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/jabezwinston/dcouver',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development :: Version Control',
        'Topic :: Office/Business :: Office Suites',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        # No external dependencies - uses Python standard library only
    ],
    extras_require={
        'completions': [
            'argcomplete>=1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'docuver=docuver.cli:main',
        ],
    },
    keywords='version-control office documents docx xlsx odt ods odp meta-tool git',
    license='MIT',
    project_urls={
        'Bug Reports': 'https://github.com/jabezwinston/docuver/issues',
        'Source': 'https://github.com/jabezwinston/docuver',
    },
)
