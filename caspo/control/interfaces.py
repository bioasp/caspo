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

class IMultiScenarioReader(core.ICsvReader):
    """
    """

class IMultiScenario(interface.Interface):
    """
    """
    constraints = interface.Attribute("")
    goals = interface.Attribute("")
    exclude = interface.Attribute("")
    
    def __iter__(self):
        """"""

class IController(interface.Interface):
    """
    Controller of logical networks
    """
    
    def control(self, size):
        """"""

    def __iter__(self):
        """"""

class IStrategy(interface.Interface):
    """
    """
    
class IStrategySet(interface.Interface):
    """
    """
