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

class IBooleLogicBehavior(core.IBooleLogicNetwork):
    """
    """
    
    networks = interface.Attribute("")

class IBooleLogicBehaviorSet(core.IBooleLogicNetworkSet):
    """
    """
    
    networks = interface.Attribute("")
    dataset = interface.Attribute("")
    setup = interface.Attribute("")
    active_cues = interface.Attribute("")
    inactive_cues = interface.Attribute("")
    
    def core(self):
        """"""
    
    def mse(self, data, time):
        """"""
        
    def variances(self):
        """"""
    
class IStats(interface.Interface):
    """
    """
    
    def frequencies(self):
        """"""
        
    def frequency(self, key):
        """"""
        
    def combinatorics(self):
        """"""
