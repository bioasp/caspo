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

version = '2.0.0dev'

setup(name='caspo',
      version=version,
      description="Reasoning on the response of logical signaling networks with Answer Set Programming",
      long_description="""\
""",
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
      url='',
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
