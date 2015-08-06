# Copyright (c) 2014, Santiago Videla
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

version = '2.2.0'

long_desc = """
The aim of caspo is to implement a pipeline for automated reasoning on logical signaling networks. 
Main features include, learning of logical networks from experiments, design new experiments in 
order to reduce the uncertainty, and finding intervention strategies to control the biological system.
For more details visit `caspo's website`_.

.. _`caspo's website`: http://bioasp.github.io/caspo/

"""
setup(name='caspo',
      version=version,
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
      author='Santiago Videla',
      author_email='santiago.videla@gmail.com',
      url='http://bioasp.github.io/caspo/',
      license='GPLv3+',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "zope.component",
          "zope.interface",
          "pyzcasp",
          "numpy",
          "networkx",
          "pyparsing>=1.5.7,<2.0.0", #latest pyparsing version for Python 2.x
          "pydot"
      ],
      entry_points={
          'console_scripts': [
              'caspo=caspo.console.main:run',
          ]
      }
      )
