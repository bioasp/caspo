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
from pyzcasp import asp
from caspo import core

class IConstraintsReader(core.ICsvReader):
    """
    Marker interface
    """

class IGoalsReader(core.ICsvReader):
    """
    Marker interface
    """
    
class IConstraints(interface.Interface):
    """
    """
    
    def iteritems(self):
        """"""
        
class IGoals(interface.Interface):
    """
    """
    
    def iteritems(self):
        """"""

class IScenario(interface.Interface):
    """
    """
    
    constraints = interface.Attribute("Side constraints")
    goals = interface.Attribute("Goals")

class IMultiScenario(interface.Interface):
    """
    """
    
    scenarios = interface.Attribute("")

class IController(interface.Interface):
    """
    Controller of logical networks
    """
    
    def control(self, size):
        """"""

    def __iter__(self):
        """"""
