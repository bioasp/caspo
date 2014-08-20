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

from zope import interface
from caspo import core
    
class IDiscretization(interface.Interface):
    """
    Dicretization function
    """
    
    factor = interface.Attribute("Discretization factor")
    
    def __call__(self, data):
        """"""
        
class IDiscreteDataset(interface.Interface):
    """
    Discrete dataset
    """
    
    dataset = interface.Attribute("Raw dataset")
    discretize = interface.Attribute("Discretize funciton")
    
    def at(self, time):
        """"""
                
class ILearner(interface.Interface):
    """
    Learner of Boolean logic models
    """
    
    def learn(self, fit, size):
        """"""
        
    def random(self, n, size, nand, maxin):
        """"""
        