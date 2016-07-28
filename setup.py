# Copyright (c) 2014-2016, Santiago Videla
#
# This file is part of caspo.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caspo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

from caspo import __package__, __author__, __email__, __license__, __version__

long_desc = """
The aim of caspo is to implement a pipeline for automated reasoning on logical signaling networks. 
Main features include, learning of logical networks from experiments, design new experiments in 
order to reduce the uncertainty, and finding intervention strategies to control the biological system.
For more details visit `caspo's website`_.

.. _`caspo's website`: http://bioasp.github.io/caspo/

"""
setup(name=__package__,
      version=__version__,
      description="Reasoning on the response of logical signaling networks with Answer Set Programming",
      long_description=long_desc + open('CHANGES').read(),
      classifiers=["Intended Audience :: Science/Research", 
                   "Intended Audience :: Healthcare Industry",
                   "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2.7",
                   "Topic :: Scientific/Engineering :: Artificial Intelligence",
                   "Topic :: Scientific/Engineering :: Bio-Informatics"
                   ], 
                   # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='logical signaling networks systems biology answer set programming',
      author=__author__,
      author_email=__email__,
      url='http://bioasp.github.io/caspo/',
      license=__license__,
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "networkx",
          "pyparsing",
          "pydotplus",
          "joblib"
      ],
      entry_points={
          'console_scripts': [
              'caspo=caspo.console.main:run',
          ]
      }
      )
