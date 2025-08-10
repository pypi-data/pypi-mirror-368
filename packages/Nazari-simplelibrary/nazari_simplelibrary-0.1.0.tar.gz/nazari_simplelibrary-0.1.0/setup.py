# -*- coding: utf-8 -*-
"""
Created on Fri Aug  8 11:46:50 2025
setup.py file
@author: Mahjoobe Nazari
"""
from setuptools import setup , find_packages

setup(name="Nazari-simplelibrary",
    version="0.1.0",
    description="A simple library management system",
    author="Mahjoobe Nazari",
    author_email="m.nazari24@gmail.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',)
