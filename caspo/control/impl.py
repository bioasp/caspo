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
from collections import namedtuple
from zope import interface

from caspo import core

from interfaces import *

class ConstraintsList(list):
    interface.implements(core.IClampingList)
    
    @property
    def clampings(self):
        return self

class GoalsList(list):
    interface.implements(core.IClampingList)
    
    @property
    def clampings(self):
        return self

class Strategy(core.Clamping):
    interface.implements(IStrategy)
    
    def __init__(self, literals=[]):
        super(Strategy, self).__init__(literals)
        
class StrategySet(set):
    interface.implements(IStrategySet)
