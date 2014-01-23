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
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.import random
# -*- coding: utf-8 -*-

from zope import interface
from caspo import core
    
class IMidasReader(core.IFileReader):
    """
    MIDAS file reader
    """
    stimuli = interface.Attribute("Stimuli cues")
    inhibitors = interface.Attribute("Inhibitors cues")
    readouts = interface.Attribute("Readouts")

class IDiscretization(interface.Interface):
    """
    Dicretization function
    """
    
    factor = interface.Attribute("Discretization factor")
    
    def __call__(self, data):
        """"""
        
class ITimePoint(interface.Interface):
    """
    """
    
class IDataset(interface.Interface):
    """
    Experimental dataset
    """
    
    setup = interface.Attribute("Experimental setup")
    cues = interface.Attribute("Iterable over experimental cues")
    readouts = interface.Attribute("Iterable over experimental readouts")
    factor = interface.Attribute("Factor used during discretization")
    
    def __iter__(self):
        """"""

class IGraphCompressor(interface.Interface):
    """
    """
    
    def compress(self, graph, setup):
        """
        """
        
class ILearner(interface.Interface):
    """
    Learner of Boolean logic models
    """
    
    def learn(self, fit, size):
        """"""

    def __iter__(self):
        """"""