#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
from io import open

about = {}
# Read version number from anthroab.__version__.py (see PEP 396)
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'anthroab', '__version__.py'), encoding='utf-8') as f:
    exec(f.read(), about)

# Read contents of readme file into string
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='anthroab',
    version=about['__version__'],
    description='AnthroAb: Human antibody language model based on RoBERTa for humanization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Hemant Nagar',
    packages=find_packages(),
    author_email='hn533621@ohio.edu',
    license='MIT',
    python_requires=">=3.10",
    install_requires=[
        'pandas>=1.0.0',
        'transformers>=4.0.0',
        'torch>=1.7.0',
        'numpy>=1.19.0',
    ],
    keywords='anthroab, antibody humanization, roberta, biophi, antibody design, bioinformatics, protein engineering',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    url='https://github.com/nagarh/AnthroAb',
    project_urls={
        'Bug Reports': 'https://github.com/nagarh/AnthroAb/issues',
        'Source': 'https://github.com/nagarh/AnthroAb',
        'Documentation': 'https://github.com/nagarh/AnthroAb',
        'Download': 'https://github.com/nagarh/AnthroAb/releases',
    },
    zip_safe=False,
) 